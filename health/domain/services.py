"""Servicios de dominio para el contexto Health."""
from health.domain.entities import HealthStatus


class HealthCheckService:
    """
    Servicio de dominio que contiene la lógica de negocio pura
    para clasificar estados de salud.
    """
    
    @staticmethod
    def classify_memory_usage(percent: float) -> str:
        """
        Clasifica el uso de memoria.
        
        - > 90% → unhealthy
        - > 75% → degraded
        - <= 75% → healthy
        
        Args:
            percent: Porcentaje de uso de memoria.
            
        Returns:
            Estado ('healthy', 'degraded', 'unhealthy').
        """
        if percent > 90:
            return HealthStatus.UNHEALTHY
        elif percent > 75:
            return HealthStatus.DEGRADED
        else:
            return HealthStatus.HEALTHY
    
    @staticmethod
    def classify_database_latency(latency_ms: float) -> str:
        """
        Clasifica la latencia de base de datos.
        
        - > 5000ms → unhealthy
        - > 1000ms → degraded
        - <= 1000ms → healthy
        
        Args:
            latency_ms: Latencia en milisegundos.
            
        Returns:
            Estado ('healthy', 'degraded', 'unhealthy').
        """
        if latency_ms > 5000:
            return HealthStatus.UNHEALTHY
        elif latency_ms > 1000:
            return HealthStatus.DEGRADED
        else:
            return HealthStatus.HEALTHY
    
    @staticmethod
    def classify_disk_usage(percent: float) -> str:
        """
        Clasifica el uso de disco.
        
        - > 90% → unhealthy
        - > 75% → degraded
        - <= 75% → healthy
        
        Args:
            percent: Porcentaje de uso de disco.
            
        Returns:
            Estado ('healthy', 'degraded', 'unhealthy').
        """
        if percent > 90:
            return HealthStatus.UNHEALTHY
        elif percent > 75:
            return HealthStatus.DEGRADED
        else:
            return HealthStatus.HEALTHY
