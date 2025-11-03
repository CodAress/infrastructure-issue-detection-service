"""Modelos ORM (Peewee) para el contexto de Detection."""
from datetime import datetime
from peewee import Model, CharField, TextField, FloatField, IntegerField, DateTimeField, BooleanField
from shared.infrastructure.database import db


class ConsultaAnalisisModel(Model):
    """
    Modelo ORM que representa una ConsultaAnalisis persistida en la BD.
    
    Mapeo:
    - uuid_consulta → Identificador único (PK)
    - url_imagen → URL de la imagen original
    - client_id → Cliente que solicitó
    - estado → Pendiente, procesando, completado, error
    - categoria → Resultado de categoría detectada
    - confianza → Confianza del modelo
    - url_resultado → URL de imagen anotada en Cloudinary
    - num_detecciones → Cantidad de instancias detectadas
    - error_mensaje → Mensaje de error si falló
    - created_at / updated_at → Timestamps
    """
    
    uuid_consulta = CharField(primary_key=True, max_length=36)
    url_imagen = TextField()
    client_id = CharField(max_length=100)
    
    # Estado: pendiente, procesando, completado, error
    estado = CharField(max_length=20, default='pendiente')
    
    # Resultados de detección
    categoria = CharField(max_length=50, null=True)
    confianza = FloatField(null=True)
    url_resultado = TextField(null=True)
    num_detecciones = IntegerField(default=0)
    
    # Error
    error_mensaje = TextField(null=True)
    
    # Auditoría
    created_at = DateTimeField(default=datetime.utcnow)
    updated_at = DateTimeField(default=datetime.utcnow)
    
    class Meta:
        """Información meta del modelo."""
        database = db
        table_name = 'consultas_analisis'
        indexes = (
            (('client_id', 'created_at'), False),
            (('estado',), False),
        )


class DetalleDeteccionModel(Model):
    """
    Modelo ORM para almacenar detalles granulares de una detección.
    
    Permite analizar:
    - Métricas por componente
    - Análisis temporal
    - Patrones de detección
    """
    
    consulta_analisis = CharField(max_length=36)  # Referencia a uuid_consulta
    modelo_version = CharField(max_length=20)     # ej: best.pt
    imgsz = IntegerField(default=640)
    umbral_confianza = FloatField()
    clases_encontradas = TextField()              # JSON serializado
    confianzas_raw = TextField(null=True)         # JSON serializado: [0.95, 0.87, ...]
    tiempo_inferencia_ms = IntegerField()
    
    created_at = DateTimeField(default=datetime.utcnow)
    
    class Meta:
        """Información meta del modelo."""
        database = db
        table_name = 'detalles_detecciones'
        indexes = (
            (('consulta_analisis',), False),
        )
