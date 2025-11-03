"""Repositorio para gestionar entidades de Cliente en el contexto de IAM."""
from typing import Optional
from datetime import datetime

import peewee

from iam.domain.entities import Client
from iam.infrastructure.models import Client as ClientModel
from shared.domain.exceptions import ConflictException


class ClientRepository:
    """
    Repositorio para gestionar entidades de Cliente en el contexto de IAM.
    
    Maneja todas las operaciones de persistencia de clientes (servicios backend).
    """
    
    @staticmethod
    def find_by_id_and_api_key(client_id: str, api_key: str) -> Optional[Client]:
        """
        Busca un cliente por su ID y clave API.
        
        Args:
            client_id: El ID del cliente.
            api_key: La clave API del cliente.
            
        Returns:
            Cliente si es encontrado y válido, None en caso contrario.
        """
        try:
            client_model = ClientModel.get(
                (ClientModel.client_id == client_id) & 
                (ClientModel.api_key == api_key)
            )
            return ClientRepository._model_to_entity(client_model)
        except peewee.DoesNotExist:
            return None

    @staticmethod
    def find_by_api_key(api_key: str) -> Optional[Client]:
        """
        Busca un cliente por su API Key.
        
        Args:
            api_key: La clave API del cliente.
            
        Returns:
            Cliente si es encontrado, None en caso contrario.
        """
        try:
            client_model = ClientModel.get(ClientModel.api_key == api_key)
            return ClientRepository._model_to_entity(client_model)
        except peewee.DoesNotExist:
            return None

    @staticmethod
    def find_by_id(client_id: str) -> Optional[Client]:
        """
        Busca un cliente por su ID.
        
        Args:
            client_id: El ID del cliente.
            
        Returns:
            Cliente si es encontrado, None en caso contrario.
        """
        try:
            client_model = ClientModel.get(ClientModel.client_id == client_id)
            return ClientRepository._model_to_entity(client_model)
        except peewee.DoesNotExist:
            return None

    @staticmethod
    def create(client_id: str, api_key: str, name: str) -> Client:
        """
        Crea un nuevo cliente en la base de datos.
        
        Args:
            client_id: Identificador único del cliente.
            api_key: Clave API del cliente.
            name: Nombre descriptivo del cliente.
            
        Returns:
            Entidad Cliente creada.
            
        Raises:
            ConflictException: Si el client_id o api_key ya existen.
        """
        try:
            now = datetime.utcnow()
            client_model = ClientModel.create(
                client_id=client_id,
                api_key=api_key,
                name=name,
                is_active=True,
                created_at=now,
                updated_at=now
            )
            return ClientRepository._model_to_entity(client_model)
        except peewee.IntegrityError:
            raise ConflictException(
                f"El cliente con ID '{client_id}' o clave API ya existe"
            )

    @staticmethod
    def update(client_id: str, name: str = None, is_active: bool = None) -> Optional[Client]:
        """
        Actualiza un cliente existente.
        
        Args:
            client_id: ID del cliente a actualizar.
            name: Nuevo nombre del cliente (opcional).
            is_active: Nuevo estado del cliente (opcional).
            
        Returns:
            Cliente actualizado si existe, None en caso contrario.
        """
        try:
            client_model = ClientModel.get(ClientModel.client_id == client_id)
            if name is not None:
                client_model.name = name
            if is_active is not None:
                client_model.is_active = is_active
            client_model.updated_at = datetime.utcnow()
            client_model.save()
            return ClientRepository._model_to_entity(client_model)
        except peewee.DoesNotExist:
            return None

    @staticmethod
    def delete(client_id: str) -> bool:
        """
        Elimina un cliente de la base de datos.
        
        Args:
            client_id: ID del cliente a eliminar.
            
        Returns:
            True si se eliminó, False si no existe.
        """
        try:
            client_model = ClientModel.get(ClientModel.client_id == client_id)
            client_model.delete_instance()
            return True
        except peewee.DoesNotExist:
            return False

    @staticmethod
    def get_all_active() -> list:
        """
        Obtiene todos los clientes activos.
        
        Returns:
            Lista de clientes activos.
        """
        clients = ClientModel.select().where(ClientModel.is_active == True)
        return [ClientRepository._model_to_entity(client) for client in clients]

    @staticmethod
    def get_or_create_test_client() -> Client:
        """
        Crea u obtiene un cliente de prueba para propósitos de testing y desarrollo.
        
        Returns:
            Entidad Cliente de prueba.
        """
        now = datetime.utcnow()
        client, _ = ClientModel.get_or_create(
            client_id="detection-client-test",
            defaults={
                "api_key": "test-api-key-detection-12345-secure",
                "name": "Test Detection Client",
                "is_active": True,
                "created_at": now,
                "updated_at": now
            }
        )
        return ClientRepository._model_to_entity(client)

    @staticmethod
    def _model_to_entity(client_model: ClientModel) -> Client:
        """
        Convierte un modelo ORM a una entidad de dominio.
        
        Args:
            client_model: Modelo ORM del cliente.
            
        Returns:
            Entidad Cliente del dominio.
        """
        return Client(
            client_id=client_model.client_id,
            api_key=client_model.api_key,
            name=client_model.name,
            is_active=client_model.is_active,
            created_at=client_model.created_at,
            updated_at=client_model.updated_at
        )
