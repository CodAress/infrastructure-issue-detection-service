"""Entidades de dominio para el contexto de IAM."""
from datetime import datetime
from typing import Optional
from shared.domain.entities import AuditableEntity


class Client(AuditableEntity):
    """
    Representa una entidad cliente en el contexto de IAM para el servicio de detección.
    
    Un cliente es un servicio backend externo que consume la API de detección.
    No representa usuarios finales, sino servicios que se integran con este servicio.
    
    Hereda campos de auditoría de AuditableEntity:
        created_at (datetime): Marca de tiempo de creación del cliente.
        updated_at (datetime): Marca de tiempo de última actualización del cliente.

    Atributos específicos:
        client_id (str): Identificador único del cliente (ej: backend-service).
        api_key (str): Clave API privada para autenticar las solicitudes.
        name (str): Nombre descriptivo del cliente.
        is_active (bool): Indica si el cliente está activo.
    """
    def __init__(
        self, 
        client_id: str, 
        api_key: str, 
        name: str, 
        is_active: bool = True,
        created_at: Optional[datetime] = None,
        updated_at: Optional[datetime] = None
    ):
        """
        Inicializa la entidad Cliente.
        
        Args:
            client_id: Identificador único del cliente.
            api_key: Clave API del cliente.
            name: Nombre descriptivo.
            is_active: Estado del cliente (por defecto True).
            created_at: Fecha de creación (opcional, auto-generada si no se provee).
            updated_at: Fecha de última actualización (opcional, auto-generada si no se provee).
        """
        super().__init__()
        self.client_id = client_id
        self.api_key = api_key
        self.name = name
        self.is_active = is_active
        
        # Si se proveen las fechas de auditoría, sobrescribir las del padre
        if created_at is not None:
            self.created_at = created_at
        if updated_at is not None:
            self.updated_at = updated_at

    def is_authenticated(self) -> bool:
        """
        Verifica si el cliente está activo y autenticado.
        
        Returns:
            True si el cliente está activo, False en caso contrario.
        """
        return self.is_active

    def __repr__(self) -> str:
        """
        Representación string del cliente.
        
        Returns:
            String con información del cliente.
        """
        return f"Client(client_id={self.client_id}, name={self.name}, is_active={self.is_active})"
