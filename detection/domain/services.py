"""
Domain Services for Detection BC

Servicios de Dominio para Detection BC
"""
from detection.domain.entities import CategoriaIncidencia


class DetectionService:
    """
    Servicio de dominio que contiene lógica pura de negocio
    para procesamiento de detecciones.
    
    No tiene dependencias externas (no accede a BD, APIs, etc.)
    Contiene la lógica de negocio que es independiente de tecnología
    """
    
    # Confidence thresholds (minimum required confidence by category)
    UMBRALES_MINIMOS = {
        CategoriaIncidencia.BACHE: 0.30,
        CategoriaIncidencia.BASURA_ACUMULADA: 0.40,
        CategoriaIncidencia.SEMAFORO_MALOGRADO: 0.45,
        CategoriaIncidencia.POSTE_CAIDO: 0.35,
    }
    
    @staticmethod
    def validate_confidence(categoria: str, confianza: float) -> bool:
        """
        Valida si la confianza de detección cumple con el umbral mínimo.
        
        Args:
            categoria: Categoría de incidencia
            confianza: Confianza reportada (0-1)
            
        Returns:
            True si cumple con el umbral, False en caso contrario
        """
        umbral = DetectionService.UMBRALES_MINIMOS.get(
            categoria, 
            0.30  # umbral por defecto
        )
        return confianza >= umbral
    
    @staticmethod
    def classify_severity(confianza: float) -> str:
        """
        Clasifica la severidad de una detección según su confianza.
        
        Args:
            confianza: Nivel de confianza (0-1)
            
        Returns:
            Severidad: "baja", "media", "alta", "crítica"
        """
        if confianza >= 0.85:
            return "crítica"
        elif confianza >= 0.70:
            return "alta"
        elif confianza >= 0.50:
            return "media"
        else:
            return "baja"
    
    @staticmethod
    def generate_result_tags(categoria: str, num_detecciones: int) -> dict:
        """
        Genera etiquetas y metadatos adicionales para el resultado.
        
        Args:
            categoria: Categoría detectada
            num_detecciones: Cantidad de instancias detectadas
            
        Returns:
            Diccionario con etiquetas y metadatos
        """
        return {
            "categoria": categoria,
            "instancias": num_detecciones,
            "requiere_mantenimiento": num_detecciones > 0,
            "prioridad": "alta" if num_detecciones >= 3 else "media" if num_detecciones >= 1 else "baja"
        }
