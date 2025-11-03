"""Servicio de aplicación para autenticación y gestión de clientes (servicios backend)."""
from typing import Optional

from iam.domain.entities import Client
from iam.domain.services import AuthService
from iam.infrastructure.repositories import ClientRepository
from shared.domain.exceptions import UnauthorizedException, ValidationException


class AuthApplicationService:
    """
    Servicio de aplicación para autenticación y gestión de clientes.
    
    Orquesta la validación de credenciales de servicios backend (clientes),
    usando servicios de dominio y repositorios.
    """
    def __init__(self):
        """
        Inicializa el AuthApplicationService con repositorios y servicios.
        """
        self.client_repository = ClientRepository()
        self.auth_service = AuthService()

    def authenticate(self, client_id: str, api_key: str) -> Client:
        """
        Autentica un cliente (servicio backend) usando sus credenciales.
        
        Args:
            client_id: Identificador del cliente.
            api_key: Clave API del cliente.
            
        Returns:
            Entidad Cliente si la autenticación es exitosa.
            
        Raises:
            ValidationException: Si las credenciales están vacías.
            UnauthorizedException: Si las credenciales son inválidas o el cliente está inactivo.
        """
        # Validar que las credenciales no estén vacías
        self.auth_service.validate_client_id(client_id)
        self.auth_service.validate_api_key(api_key)
        
        # Buscar cliente en la base de datos
        client = self.client_repository.find_by_id_and_api_key(client_id, api_key)
        
        # Autenticar (lanza excepción si es inválido o está inactivo)
        self.auth_service.authenticate(client)
        
        return client

    def authenticate_by_api_key(self, api_key: str) -> Client:
        """
        Autentica un cliente usando SOLO su API Key.
        
        Args:
            api_key: Clave API del cliente.
            
        Returns:
            Entidad Cliente si la autenticación es exitosa.
            
        Raises:
            ValidationException: Si el API Key está vacío.
            UnauthorizedException: Si el API Key es inválido o el cliente está inactivo.
        """
        # Validar API Key
        self.auth_service.validate_api_key(api_key)
        
        # Buscar cliente por API Key
        client = self.client_repository.find_by_api_key(api_key)
        
        # Autenticar (lanza excepción si es inválido o está inactivo)
        self.auth_service.authenticate(client)
        
        return client

    def get_or_create_test_client(self) -> Client:
        """
        Recupera u obtiene un cliente de prueba para desarrollo y testing.
        
        Returns:
            Entidad Cliente de prueba con credenciales predefinidas.
        """
        return self.client_repository.get_or_create_test_client()

    def get_or_create_backend_client(self, client_id: str, api_key: str, name: str) -> Client:
        """
        Obtiene o crea el cliente backend principal desde variables de entorno.
        
        Este método es idempotente: si el cliente ya existe, lo retorna.
        Si no existe, lo crea con las credenciales proporcionadas.
        
        Args:
            client_id: Identificador del cliente (desde BACKEND_CLIENT_ID)
            api_key: API Key del cliente (desde BACKEND_API_KEY)
            name: Nombre descriptivo (desde BACKEND_CLIENT_NAME)
            
        Returns:
            Entidad Cliente (existente o recién creado)
        """
        # Validar credenciales
        self.auth_service.validate_client_id(client_id)
        self.auth_service.validate_api_key(api_key)
        
        # Intentar obtener cliente existente
        existing_client = self.client_repository.find_by_id(client_id)
        
        if existing_client:
            # Verificar que el API Key coincida
            if existing_client.api_key != api_key:
                raise ValidationException(
                    f"Cliente '{client_id}' existe pero el API Key no coincide. "
                    "Verifica las variables de entorno."
                )
            return existing_client
        
        # Si no existe, crearlo
        return self.client_repository.create(client_id, api_key, name)

    def get_client_by_id(self, client_id: str) -> Optional[Client]:
        """
        Obtiene un cliente por su ID.
        
        Args:
            client_id: Identificador del cliente.
            
        Returns:
            Cliente si existe, None en caso contrario.
        """
        return self.client_repository.find_by_id(client_id)

    def create_client(self, client_id: str, api_key: str, name: str) -> Client:
        """
        Crea un nuevo cliente (servicio backend) en el sistema.
        
        Args:
            client_id: Identificador único del cliente.
            api_key: Clave API del cliente (mínimo 20 caracteres).
            name: Nombre descriptivo del cliente.
            
        Returns:
            Entidad Cliente creada.
            
        Raises:
            ValidationException: Si los datos son inválidos.
            ConflictException: Si el cliente_id o api_key ya existe.
        """
        # Validar datos
        self.auth_service.validate_client_id(client_id)
        self.auth_service.validate_api_key(api_key)
        
        if not name or not isinstance(name, str) or len(name) < 3:
            raise ValidationException("El nombre debe ser una cadena con mínimo 3 caracteres")
        
        # Crear cliente
        return self.client_repository.create(client_id, api_key, name)

    def update_client(self, client_id: str, name: str = None, is_active: bool = None) -> Client:
        """
        Actualiza un cliente existente.
        
        Args:
            client_id: Identificador del cliente a actualizar.
            name: Nuevo nombre (opcional).
            is_active: Nuevo estado activo/inactivo (opcional).
            
        Returns:
            Cliente actualizado.
            
        Raises:
            ValidationException: Si el nombre es inválido.
            UnauthorizedException: Si el cliente no existe.
        """
        if name is not None and (not isinstance(name, str) or len(name) < 3):
            raise ValidationException("El nombre debe ser una cadena con mínimo 3 caracteres")
        
        client = self.client_repository.update(client_id, name, is_active)
        
        if client is None:
            raise UnauthorizedException(f"Cliente '{client_id}' no encontrado")
        
        return client

    def delete_client(self, client_id: str) -> bool:
        """
        Elimina un cliente del sistema.
        
        Args:
            client_id: Identificador del cliente a eliminar.
            
        Returns:
            True si se eliminó, False si no existe.
        """
        return self.client_repository.delete(client_id)

    def get_all_active_clients(self) -> list:
        """
        Obtiene todos los clientes activos en el sistema.
        
        Returns:
            Lista de clientes activos.
        """
        return self.client_repository.get_all_active()
