"""Servicios de dominio para el contexto de IAM."""
from typing import Optional

from iam.domain.entities import Client
from shared.domain.exceptions import UnauthorizedException, ValidationException


class AuthService:
    """
    Servicio de dominio para autenticar clientes (servicios backend) en el IAM.
    
    Valida que el cliente esté activo y autorizado para acceder a los endpoints.
    """
    def __init__(self):
        """
        Constructor para AuthService.
        """
        pass

    @staticmethod
    def authenticate(client: Optional[Client]) -> bool:
        """
        Autentica un cliente verificando su existencia y estado activo.
        
        Args:
            client: Entidad Cliente o None si no existe.
            
        Returns:
            True si el cliente es válido y está activo.
            
        Raises:
            UnauthorizedException: Si el cliente no existe o está inactivo.
        """
        if client is None:
            raise UnauthorizedException("Las credenciales del cliente son inválidas o no existen")
        
        if not client.is_authenticated():
            raise UnauthorizedException(f"El cliente '{client.client_id}' está inactivo")
        
        return True

    @staticmethod
    def validate_client_id(client_id: str) -> None:
        """
        Valida que el client_id sea válido.
        
        Args:
            client_id: El ID del cliente a validar.
            
        Raises:
            ValidationException: Si el client_id es inválido.
        """
        if not client_id or not isinstance(client_id, str):
            raise ValidationException("El client_id debe ser una cadena no vacía")
        
        if len(client_id) < 3:
            raise ValidationException("El client_id debe tener al menos 3 caracteres")
        
        if len(client_id) > 100:
            raise ValidationException("El client_id debe tener máximo 100 caracteres")

    @staticmethod
    def validate_api_key(api_key: str) -> None:
        """
        Valida que la clave API sea válida.
        
        Args:
            api_key: La clave API a validar.
            
        Raises:
            ValidationException: Si la clave API es inválida.
        """
        if not api_key or not isinstance(api_key, str):
            raise ValidationException("La clave API debe ser una cadena no vacía")
        
        if len(api_key) < 20:
            raise ValidationException("La clave API debe tener al menos 20 caracteres")
        
        if len(api_key) > 255:
            raise ValidationException("La clave API debe tener máximo 255 caracteres")
