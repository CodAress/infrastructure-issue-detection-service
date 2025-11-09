"""Entidades de dominio para el contexto de Detection."""
from datetime import datetime
from typing import Optional, List
from shared.domain.entities import AuditableEntity


class CategoriaIncidencia:
    """Value Object que representa una categoría de incidencia."""
    
    # Categorías soportadas
    BACHE = "bache"
    BASURA_ACUMULADA = "basura_acumulada"
    SEMAFORO_MALOGRADO = "semaforo_malogrado"
    POSTE_CAIDO = "poste_caido"
    NINGUNA = "ninguna"  # Cuando no se detecta ninguna incidencia
    
    CATEGORIAS_VALIDAS = [BACHE, BASURA_ACUMULADA, SEMAFORO_MALOGRADO, POSTE_CAIDO, NINGUNA]
    
    def __init__(self, categoria: str):
        if categoria not in self.CATEGORIAS_VALIDAS:
            raise ValueError(f"Categoría inválida: {categoria}. Válidas: {self.CATEGORIAS_VALIDAS}")
        self.valor = categoria
    
    def __str__(self) -> str:
        return self.valor
    
    def __eq__(self, other) -> bool:
        if isinstance(other, CategoriaIncidencia):
            return self.valor == other.valor
        return self.valor == other


class ResultadoDeteccion:
    """Value Object que representa el resultado de una detección."""
    
    def __init__(self, categoria: str, confianza: float, url_resultado: str, 
                 num_detecciones: int = 0, detalles: dict = None):
        """
        Args:
            categoria: Categoría detectada (bache, basura, etc.)
            confianza: Nivel de confianza (0-1)
            url_resultado: URL de la imagen procesada en Cloudinary
            num_detecciones: Cantidad de instancias detectadas
            detalles: Datos adicionales del análisis
        """
        self.categoria = CategoriaIncidencia(categoria)
        self.confianza = float(confianza)
        self.url_resultado = url_resultado
        self.num_detecciones = int(num_detecciones)
        self.detalles = detalles or {}
        self.timestamp = datetime.utcnow()
    
    def to_dict(self) -> dict:
        return {
            "categoria": str(self.categoria),
            "confianza": round(self.confianza, 4),
            "url_resultado": self.url_resultado,
            "num_detecciones": self.num_detecciones,
            "timestamp": self.timestamp.isoformat(),
            "detalles": self.detalles
        }


class ConsultaAnalisis(AuditableEntity):
    """
    Entidad raíz del agregado Detection.
    
    Representa un análisis solicitado por el backend principal.
    Tiene un UUID único generado externamente para identificar la consulta.
    
    Hereda campos de auditoría:
    - created_at / created_by: Cuándo y quién creó
    - updated_at / updated_by: Cuándo y quién actualizó
    - deleted_at / deleted_by: Cuándo y quién eliminó (soft delete)
    - is_deleted: Indicador de eliminación lógica
    """
    
    PENDIENTE = "pendiente"
    PROCESANDO = "procesando"
    COMPLETADO = "completado"
    ERROR = "error"
    
    ESTADOS_VALIDOS = [PENDIENTE, PROCESANDO, COMPLETADO, ERROR]
    
    def __init__(self, uuid_consulta: str, url_imagen: str, client_id: str):
        """
        Inicializa una nueva ConsultaAnalisis.
        
        Args:
            uuid_consulta: UUID único generado por backend principal
            url_imagen: URL de la imagen a analizar (desde backend principal)
            client_id: ID del cliente que solicitó el análisis
        """
        super().__init__()  # Inicializa campos de auditoría
        
        self.uuid_consulta = uuid_consulta
        self.url_imagen = url_imagen
        self.client_id = client_id
        self.estado = self.PENDIENTE
        self.resultado: Optional[ResultadoDeteccion] = None
        self.error_mensaje: Optional[str] = None
    
    def mark_processing(self) -> None:
        """Marca la consulta como en procesamiento."""
        if self.estado != self.PENDIENTE:
            raise ValueError(f"No se puede marcar como PROCESANDO desde estado: {self.estado}")
        self.estado = self.PROCESANDO
        self.mark_updated()
    
    def mark_completed(self, resultado: ResultadoDeteccion) -> None:
        """Marca la consulta como completada con su resultado."""
        self.estado = self.COMPLETADO
        self.resultado = resultado
        self.mark_updated()
    
    def mark_error(self, mensaje_error: str) -> None:
        """Marca la consulta como error."""
        self.estado = self.ERROR
        self.error_mensaje = mensaje_error
        self.mark_updated()
    
    def is_completed(self) -> bool:
        """Verifica si la consulta fue completada exitosamente."""
        return self.estado == self.COMPLETADO
    
    def is_pending(self) -> bool:
        """Verifica si la consulta está pendiente."""
        return self.estado == self.PENDIENTE
    
    def to_dict(self) -> dict:
        """Convierte la entidad a diccionario excluyendo campos nulos."""
        result = {
            "uuid_consulta": self.uuid_consulta,
            "url_imagen": self.url_imagen,
            "client_id": self.client_id,
            "estado": self.estado,
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "updated_at": self.updated_at.isoformat() if self.updated_at else None,
        }
        
        # Solo incluir resultado si existe
        if self.resultado:
            result["resultado"] = self.resultado.to_dict()
        
        # Solo incluir error si existe
        if self.error_mensaje:
            result["error"] = self.error_mensaje
        
        return result
