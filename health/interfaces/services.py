"""Capa de Interfaces - Endpoints HTTP para Health."""
from datetime import datetime
from flask import Blueprint, jsonify, request

from health.application.services import HealthApplicationService
from shared.domain.exceptions import DomainException
from shared.infrastructure.error_mapper import ErrorMapper

health_api = Blueprint('health_api', __name__, url_prefix='/api/v1/health')

# Global reference to the application service (set via set_health_service)
_health_service: HealthApplicationService = None


def set_health_service(service: HealthApplicationService) -> None:
    """
    Configura el servicio de aplicación (inyección de dependencias).
    
    Debe ser llamado desde app.py durante la inicialización.
    
    Args:
        service: Instancia de HealthApplicationService
    """
    global _health_service
    _health_service = service


def get_health_service() -> HealthApplicationService:
    """
    Obtiene la instancia del servicio de aplicación.
    
    Returns:
        HealthApplicationService configurado
        
    Raises:
        RuntimeError: Si el servicio no ha sido configurado
    """
    if _health_service is None:
        raise RuntimeError("Health service no configurado. Llamar set_health_service()")
    return _health_service


@health_api.route('', methods=['GET'])
def get_health():
    """
    Get health status of the service
    ---
    tags:
      - Health
    parameters:
      - name: detailed
        in: query
        type: boolean
        default: false
        description: Include complete diagnostic
    responses:
      200:
        description: Service is healthy
        schema:
          type: object
          properties:
            service:
              type: string
            status:
              type: string
              enum: [healthy, degraded, unhealthy]
            components:
              type: object
      503:
        description: Service is degraded or unhealthy
    """
    try:
        is_detailed = request.args.get('detailed', 'false').lower() == 'true'
        
        service = get_health_service()
        if is_detailed:
            health_data = service.get_health()
        else:
            health_data = service.get_quick_health()
        
        status_code = 200 if service.is_healthy() else 503
        return jsonify(health_data), status_code
    
    except Exception as e:
        return jsonify({
            "service": "infrastructure-issue-detection-service",
            "status": "unhealthy",
            "message": f"Health check failed: {str(e)}"
        }), 503


@health_api.route('/readiness', methods=['GET'])
def get_readiness_probe():
    """
    Kubernetes readiness probe
    ---
    tags:
      - Health
    responses:
      200:
        description: Service is ready to receive traffic
      503:
        description: Service is not ready
    """
    try:
        service = get_health_service()
        health_data = service.get_quick_health()
        status_code = 200 if service.is_ready() else 503
        return jsonify(health_data), status_code
    
    except Exception as e:
        return jsonify({
            "service": "infrastructure-issue-detection-service",
            "status": "unhealthy",
            "message": f"Readiness check failed: {str(e)}"
        }), 503


@health_api.route('/liveness', methods=['GET'])
def get_liveness_probe():
    """
    Kubernetes liveness probe
    ---
    tags:
      - Health
    responses:
      200:
        description: Service is alive
      503:
        description: Service is dead
    """
    try:
        service = get_health_service()
        is_alive = service.is_alive()
        status_code = 200 if is_alive else 503
        
        return jsonify({
            "service": "infrastructure-issue-detection-service",
            "status": "alive" if is_alive else "dead",
            "timestamp": datetime.utcnow().isoformat()
        }), status_code
    
    except Exception as e:
        return jsonify({
            "service": "infrastructure-issue-detection-service",
            "status": "dead",
            "message": str(e)
        }), 503


@health_api.route('/components/<component_name>', methods=['GET'])
def get_component_health(component_name: str):
    """
    GET /api/v1/health/components/{component_name}
    
    Obtiene el estado de un componente específico.
    
    Parámetros:
        component_name: Nombre del componente (database, iam, memory, disk, api)
    
    PROPÓSITO:
    - Debugging y troubleshooting
    - Monitoreo granular
    - Identificar componentes fallidos
    
    Returns:
        JSON con estado del componente o 404 si no existe.
        
    HTTP Codes:
        200: Componente encontrado
        404: Componente no existe
        503: Error en el check
    """
    try:
        service = get_health_service()
        component_health = service.get_component_health(component_name)
        
        if component_health is None:
            response, status_code = ErrorMapper.handle_not_found(
                f"Componente '{component_name}' no encontrado"
            )
            return jsonify(response), status_code
        
        status_code = 200 if component_health['status'] == 'healthy' else 503
        return jsonify(component_health), status_code
    
    except Exception as e:
        response, status_code = ErrorMapper.handle_exception(e, "get_component_health")
        return jsonify(response), status_code


@health_api.route('/diagnostics', methods=['POST'])
def get_diagnostics():
    """
    Run exhaustive service diagnostics
    ---
    tags:
      - Health
    parameters:
      - in: body
        name: body
        schema:
          type: object
          properties:
            components:
              type: array
              items:
                type: string
              example: [database, memory]
    responses:
      200:
        description: Diagnostic completed
      500:
        description: Error during diagnostics
    """
    try:
        data = request.get_json() or {}
        components = data.get('components')
        
        service = get_health_service()
        if components:
            health_data = service.get_quick_health(components)
        else:
            health_data = service.get_health()
        
        return jsonify(health_data), 200
    
    except Exception as e:
        response, status_code = ErrorMapper.handle_exception(e, "get_diagnostics")
        return jsonify(response), status_code


__all__ = ["health_api"]
