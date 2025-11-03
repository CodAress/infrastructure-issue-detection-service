"""Capa de interfaz para el contexto de IAM - Autenticación de clientes backend."""
from functools import wraps
from flask import Blueprint, request, jsonify

from iam.application.services import AuthApplicationService
from shared.domain.exceptions import DomainException
from shared.infrastructure.error_mapper import ErrorMapper

iam_api = Blueprint('iam_api', __name__, url_prefix='/api/v1/clients')

# Global reference to the application service (set via set_auth_service)
_auth_service: AuthApplicationService = None


def set_auth_service(service: AuthApplicationService) -> None:
    """
    Configura el servicio de aplicación (inyección de dependencias).
    
    Debe ser llamado desde app.py durante la inicialización.
    
    Args:
        service: Instancia de AuthApplicationService
    """
    global _auth_service
    _auth_service = service


def get_auth_service() -> AuthApplicationService:
    """
    Obtiene la instancia del servicio de aplicación.
    
    Returns:
        AuthApplicationService configurado
        
    Raises:
        RuntimeError: Si el servicio no ha sido configurado
    """
    if _auth_service is None:
        raise RuntimeError("Auth service no configurado. Llamar set_auth_service()")
    return _auth_service


def authenticate_request(f):
    """
    Decorador para autenticar solicitudes de clientes (servicios backend).
    
    Verifica SOLO headers: X-API-Key
    
    Returns:
        Función decorada que autentica la solicitud.
    """
    @wraps(f)
    def decorated_function(*args, **kwargs):
        try:
            # Extraer credenciales SOLO de headers
            api_key = request.headers.get('X-API-Key')
            
            if not api_key:
                raise DomainException(
                    "Missing X-API-Key header",
                    error_code="MISSING_API_KEY"
                )
            
            # Autenticar usando solo el API Key
            service = get_auth_service()
            client = service.authenticate_by_api_key(api_key)
            
            # Pasar el cliente a la función protegida
            return f(client, *args, **kwargs)
        
        except DomainException as e:
            # Las excepciones de dominio son capturadas aquí y convertidas a respuesta HTTP
            response, status_code = ErrorMapper.handle_exception(e)
            return jsonify(response), status_code
    
    return decorated_function


@iam_api.route('', methods=['POST'])
@authenticate_request
def create_client(client):
    """
    Create a new backend client (ADMIN operation)
    ---
    tags:
      - IAM
    parameters:
      - in: header
        name: X-API-Key
        type: string
        required: true
        description: Admin API Key for creating clients
        example: admin-api-key-12345
      - in: body
        name: body
        schema:
          type: object
          required:
            - client_id
            - api_key
            - name
          properties:
            client_id:
              type: string
              description: Unique identifier for new client
              example: backend-service
            name:
              type: string
              description: Descriptive name for new client
              example: Mi Servicio Backend
            api_key:
              type: string
              description: API Key for new client (min 20 chars)
              example: clave-secreta-123-muy-larga
    responses:
      201:
        description: Client created successfully
      409:
        description: Client already exists
      400:
        description: Invalid data
      401:
        description: Not authenticated (requires admin X-API-Key header)
    security:
      - X-API-Key: []
    """
    try:
        data = request.get_json() or {}
        
        client_id = data.get('client_id')
        name = data.get('name')
        api_key = data.get('api_key')
        
        service = get_auth_service()
        client_obj = service.create_client(client_id, api_key, name)
        
        return jsonify({
            "success": True,
            "message": f"Cliente '{client_obj.client_id}' creado exitosamente",
            "client": {
                "client_id": client_obj.client_id,
                "name": client_obj.name,
                "is_active": client_obj.is_active,
                "api_key": client_obj.api_key
            }
        }), 201
    
    except DomainException as e:
        response, status_code = ErrorMapper.handle_exception(e)
        return jsonify(response), status_code


@iam_api.route('/<client_id>', methods=['GET'])
@authenticate_request
def get_client(client, client_id: str):
    """
    Get client information
    ---
    tags:
      - IAM
    parameters:
      - name: client_id
        in: path
        type: string
        required: true
        example: backend-service
    responses:
      200:
        description: Client found
      404:
        description: Client not found
      401:
        description: Not authenticated (requires X-API-Key header)
    security:
      - X-API-Key: []
    """
    try:
        service = get_auth_service()
        client_obj = service.get_client_by_id(client_id)
        
        if not client_obj:
            response, status_code = ErrorMapper.handle_not_found(
                f"Cliente '{client_id}' no encontrado"
            )
            return jsonify(response), status_code
        
        return jsonify({
            "success": True,
            "client": {
                "client_id": client_obj.client_id,
                "name": client_obj.name,
                "is_active": client_obj.is_active
            }
        }), 200
    
    except DomainException as e:
        response, status_code = ErrorMapper.handle_exception(e)
        return jsonify(response), status_code


@iam_api.route('/verify', methods=['GET'])
@authenticate_request
def verify_credentials(client):
    """
    Verify client credentials (verifica que la autenticación funciona)
    ---
    tags:
      - IAM
    parameters:
      - in: header
        name: X-API-Key
        type: string
        required: true
        description: API Key del cliente a verificar
        example: bk_live_7xK9mN2pQ4rT6wY8zA1bC3dE5fG7hJ9kL2mN4pR6sT8vW0xZ2aB4cD6eF8gH0iJ2kL4mN6p
    responses:
      200:
        description: Credentials valid - authentication successful
        schema:
          type: object
          properties:
            success:
              type: boolean
              example: true
            message:
              type: string
              example: Credenciales válidas
            client:
              type: object
              properties:
                client_id:
                  type: string
                  example: backend-reportes-infrastructure-2025
                name:
                  type: string
                  example: Backend Principal - Sistema de Reportes
                is_active:
                  type: boolean
                  example: true
      401:
        description: Invalid credentials
    security:
      - X-API-Key: []
    """
    return jsonify({
        "success": True,
        "message": "Credenciales válidas - Autenticación exitosa",
        "client": {
            "client_id": client.client_id,
            "name": client.name,
            "is_active": client.is_active
        }
    }), 200


__all__ = ["iam_api", "authenticate_request", "set_auth_service"]
