"""
Interfaces Layer - HTTP Endpoints for Detection BC

Capa de Interfaces - Endpoints HTTP para Detection BC
"""
from flask import Blueprint, jsonify, request
import os
import logging

from detection.application.services import DetectionApplicationService
from detection.infrastructure.services import YoloInferenceService, CloudinaryService
from iam.interfaces.services import authenticate_request
from shared.domain.exceptions import DomainException, ValidationException
from shared.infrastructure.error_mapper import ErrorMapper

logger = logging.getLogger(__name__)

detection_api = Blueprint('detection_api', __name__, url_prefix='/api/v1/detecciones')

# Global reference to the application service (set via set_detection_service)
_detection_service: DetectionApplicationService = None


def set_detection_service(service: DetectionApplicationService) -> None:
    """
    Configura el servicio de aplicación (inyección de dependencias).
    
    Debe ser llamado desde app.py durante la inicialización.
    
    Args:
        service: Instancia de DetectionApplicationService
    """
    global _detection_service
    _detection_service = service
    logger.info("✅ Servicio de Detection inyectado correctamente")


def get_detection_service() -> DetectionApplicationService:
    """
    Obtiene la instancia del servicio de aplicación.
    
    Returns:
        DetectionApplicationService configurado
        
    Raises:
        RuntimeError: Si el servicio no ha sido configurado
    """
    if _detection_service is None:
        raise RuntimeError("Detection service no configurado. Llamar set_detection_service()")
    return _detection_service


@detection_api.route('', methods=['POST'])
@authenticate_request
def create_analysis_request(client):
    """
    Create new infrastructure incident analysis
    ---
    tags:
      - Detection
    parameters:
      - in: header
        name: X-API-Key
        type: string
        required: true
        description: API Key del cliente (autenticación)
        example: test-api-key-detection-12345-secure
      - in: body
        name: body
        schema:
          type: object
          required:
            - uuid_consulta
            - url_imagen
          properties:
            uuid_consulta:
              type: string
              format: uuid
              description: UUID generado por backend principal
              example: 550e8400-e29b-41d4-a716-446655440000
            url_imagen:
              type: string
              format: uri
              description: URL de la imagen a analizar
              example: https://ejemplo.com/imagen.jpg
    responses:
      201:
        description: Analysis request created successfully
      400:
        description: Invalid data (missing uuid_consulta or url_imagen)
      401:
        description: Authentication failed (invalid or missing X-API-Key)
      409:
        description: UUID already exists (duplicate analysis request)
    security:
      - X-API-Key: []
    """
    try:
        service = get_detection_service()
        data = request.get_json() or {}
        
        # Recibir UUID del backend principal (NO generarlo aquí)
        uuid_consulta = data.get('uuid_consulta')
        url_imagen = data.get('url_imagen')
        
        if not uuid_consulta:
            raise ValidationException("uuid_consulta es requerido (enviado por backend principal)")
        if not url_imagen:
            raise ValidationException("url_imagen es requerida")
        
        # Validar formato de imagen (solo .jpg, .jpeg, .png)
        url_lower = url_imagen.lower()
        valid_extensions = ('.jpg', '.jpeg', '.png')
        if not any(url_lower.endswith(ext) for ext in valid_extensions):
            raise ValidationException(
                f"Formato de imagen no soportado. Solo se permiten: {', '.join(valid_extensions)}"
            )
        
        # Crear consulta con UUID proporcionado
        consulta = service.create_analysis_request(
            uuid_consulta=uuid_consulta,
            url_imagen=url_imagen,
            client_id=client.client_id
        )
        
        # Procesar inmediatamente el análisis
        try:
            logger.info(f"🚀 Iniciando procesamiento inmediato para {uuid_consulta}")
            service.execute_analysis(uuid_consulta)
            # Obtener la consulta actualizada con resultados
            consulta = service.get_analysis_request(uuid_consulta)
            logger.info(f"✅ Procesamiento completado. Estado final: {consulta.estado}")
        except Exception as e:
            logger.error(f"❌ Error ejecutando análisis para {uuid_consulta}: {e}", exc_info=True)
            # La consulta quedará en estado pendiente o error
            consulta = service.get_analysis_request(uuid_consulta)
        
        # Determinar mensaje de respuesta
        if consulta.is_completed():
            if consulta.resultado and consulta.resultado.categoria.valor == "ninguna":
                message = "Análisis completado: No se detectaron incidencias"
            else:
                message = "Análisis procesado exitosamente"
        else:
            message = "Análisis solicitado exitosamente"
        
        return jsonify({
            "success": True,
            "message": message,
            "uuid_consulta": uuid_consulta,
            "estado": consulta.estado,
            "created_at": consulta.created_at.isoformat()
        }), 201
    
    except DomainException as e:
        response, status_code = ErrorMapper.handle_exception(e)
        return jsonify(response), status_code
    except Exception as e:
        response, status_code = ErrorMapper.handle_exception(e)
        return jsonify(response), status_code


@detection_api.route('/<uuid_consulta>', methods=['GET'])
@authenticate_request
def get_analysis_result(client, uuid_consulta: str):
    """
    Get analysis result by UUID
    ---
    tags:
      - Detection
    parameters:
      - in: header
        name: X-API-Key
        type: string
        required: true
        description: API Key del cliente
      - name: uuid_consulta
        in: path
        type: string
        format: uuid
        required: true
        description: UUID único de la consulta
        example: 550e8400-e29b-41d4-a716-446655440000
    responses:
      200:
        description: Analysis found
      404:
        description: Analysis not found
      401:
        description: Not authenticated (invalid X-API-Key)
      403:
        description: Forbidden (trying to access another client's analysis)
    security:
      - X-API-Key: []
    """
    try:
        service = get_detection_service()
        
        # Obtener consulta
        consulta = service.get_analysis_request(uuid_consulta)
        
        if not consulta:
            response, status_code = ErrorMapper.handle_not_found(
                f"Análisis '{uuid_consulta}' no encontrado"
            )
            return jsonify(response), status_code
        
        # Verificar que el cliente sea propietario
        if consulta.client_id != client.client_id:
            raise ValidationException(
                "No tienes permiso para acceder a este análisis"
            )
        
        # Construir respuesta
        response_data = {
            "uuid_consulta": consulta.uuid_consulta,
            "estado": consulta.estado,
            "client_id": consulta.client_id,
            "url_imagen": consulta.url_imagen,
            "created_at": consulta.created_at.isoformat(),
            "updated_at": consulta.updated_at.isoformat()
        }
        
        # Si está completado, incluir resultado
        if consulta.is_completed() and consulta.resultado:
            response_data["resultado"] = consulta.resultado.to_dict()
            
            # Si no se detectó ninguna incidencia, agregar mensaje informativo
            if consulta.resultado.categoria.valor == "ninguna":
                response_data["message"] = "No se detectaron incidencias en la imagen"
        
        # Si hubo error, incluir mensaje
        if consulta.estado == consulta.ERROR:
            response_data["error"] = consulta.error_mensaje
        
        status_code = 200
        
        return jsonify(response_data), status_code
    
    except DomainException as e:
        response, status_code = ErrorMapper.handle_exception(e)
        return jsonify(response), status_code
    except Exception as e:
        response, status_code = ErrorMapper.handle_exception(e)
        return jsonify(response), status_code


@detection_api.route('', methods=['GET'])
@authenticate_request
def list_client_analysis_requests(client):
    """
    List all client analysis requests
    ---
    tags:
      - Detection
    parameters:
      - in: header
        name: X-API-Key
        type: string
        required: true
        description: API Key del cliente
      - name: skip
        in: query
        type: integer
        default: 0
        description: Records to skip for pagination
      - name: limit
        in: query
        type: integer
        default: 10
        description: Maximum records to return (max 100)
    responses:
      200:
        description: Successful listing - returns only client's own analysis requests
      401:
        description: Not authenticated (invalid X-API-Key)
    security:
      - X-API-Key: []
    """
    try:
        service = get_detection_service()
        
        skip = int(request.args.get('skip', 0))
        limit = int(request.args.get('limit', 10))
        
        # Limitar máximo
        limit = min(limit, 100)
        
        # Obtener solicitudes
        analysis_requests, total = service.list_client_analysis_requests(
            client.client_id,
            skip=skip,
            limit=limit
        )
        
        return jsonify({
            "success": True,
            "cliente": client.client_id,
            "total": total,
            "skip": skip,
            "limit": limit,
            "solicitudes": [r.to_dict() for r in analysis_requests]
        }), 200
    
    except Exception as e:
        response, status_code = ErrorMapper.handle_exception(e)
        return jsonify(response), status_code


# ADMIN ENDPOINT (protegido con header especial)
@detection_api.route('/_batch/process', methods=['POST'])
def process_pending_analysis_requests():
    """
    Process pending analysis requests (ADMIN)
    ---
    tags:
      - Detection
    parameters:
      - in: header
        name: X-Admin-Token
        type: string
        required: true
        description: Admin token for batch processing
        example: admin-token-123
    responses:
      200:
        description: Processing completed
        schema:
          type: object
          properties:
            processed:
              type: integer
            errors:
              type: integer
            total_processed:
              type: integer
      401:
        description: Invalid or missing admin token
      403:
        description: Forbidden - not authorized
    security:
      - X-Admin-Token: []
    """
    try:
        # Verificar admin token
        admin_token = request.headers.get('X-Admin-Token')
        expected_token = os.getenv('ADMIN_TOKEN', 'admin-secret-token')
        
        if not admin_token or admin_token != expected_token:
            return jsonify({
                "success": False,
                "error": "Invalid or missing X-Admin-Token header"
            }), 401
        
        service = get_detection_service()
        
        # Obtener análisis pendientes
        pending_requests = service.get_pending_analysis_requests()
        
        processed = 0
        errors = 0
        
        for request_item in pending_requests:
            try:
                service.execute_analysis(request_item.uuid_consulta)
                processed += 1
            except Exception as e:
                logger.error(f"Error procesando {request_item.uuid_consulta}: {e}")
                errors += 1
        
        return jsonify({
            "success": True,
            "processed": processed,
            "errors": errors,
            "total_processed": processed + errors
        }), 200
    
    except Exception as e:
        response, status_code = ErrorMapper.handle_exception(e)
        return jsonify(response), status_code


__all__ = ["detection_api"]
