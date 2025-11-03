"""Configuración de base de datos SQLite."""
import os
from peewee import SqliteDatabase

# Determinar la ruta de la base de datos
DB_PATH = os.getenv("DB_PATH", "infrastructure_issue_detection.db")
database = SqliteDatabase(DB_PATH)
# Alias para compatibilidad
db = database


def init_db(models: list = None) -> None:
    """
    Inicializa la base de datos con los modelos proporcionados.
    
    Si no se proporcionan modelos, importa automáticamente los conocidos.
    """
    if models is None:
        # Importar modelos conocidos automáticamente
        from iam.infrastructure.models import Client
        from detection.infrastructure.models import ConsultaAnalisisModel, DetalleDeteccionModel
        models = [Client, ConsultaAnalisisModel, DetalleDeteccionModel]
    
    database.connect()
    database.create_tables(models, safe=True)


def close_db() -> None:
    """Cierra la conexión a la base de datos."""
    if not database.is_closed():
        database.close()
