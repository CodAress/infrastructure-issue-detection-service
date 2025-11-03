"""Define el modelo de Cliente para el contexto de IAM."""

from peewee import Model, CharField, BooleanField, DateTimeField
from shared.infrastructure.database import db


class Client(Model):
    """
    Modelo ORM que representa un cliente (servicio backend) en la tabla 'clients'.
    
    Un cliente es un servicio backend externo que se autentica para usar
    los endpoints de detección de incidencias de infraestructura.

    Atributos:
        client_id (str): Identificador único del cliente (PK).
        api_key (str): Clave API única para autenticar solicitudes.
        name (str): Nombre descriptivo del cliente.
        is_active (bool): Indica si el cliente está activo (default: True).
        created_at (datetime): Marca de tiempo de creación.
        updated_at (datetime): Marca de tiempo de última actualización.
    """
    client_id = CharField(primary_key=True, max_length=100)
    api_key = CharField(unique=True, max_length=255)
    name = CharField(max_length=255)
    is_active = BooleanField(default=True)
    created_at = DateTimeField()
    updated_at = DateTimeField()

    class Meta:
        """Información meta para el modelo de Cliente."""
        database = db
        table_name = 'clients'
