"""Entidades de dominio para el contexto Health."""
from datetime import datetime


class HealthStatus:
    """
    Value Object que representa el estado de salud de un componente.
    
    Atributos:
        status (str): Estado del componente ('healthy', 'degraded', 'unhealthy').
        message (str): Mensaje descriptivo del estado.
        details (dict): Detalles adicionales (latencia, % uso, etc).
        checked_at (datetime): Marca de tiempo del check.
    """
    
    HEALTHY = "healthy"
    DEGRADED = "degraded"
    UNHEALTHY = "unhealthy"
    
    def __init__(self, status: str, message: str = "", details: dict = None):
        """
        Inicializa un HealthStatus.
        
        Args:
            status: Estado ('healthy', 'degraded', 'unhealthy').
            message: Mensaje del estado.
            details: Diccionario con detalles adicionales.
        """
        if status not in [self.HEALTHY, self.DEGRADED, self.UNHEALTHY]:
            raise ValueError(f"Status inválido: {status}")
        
        self.status = status
        self.message = message
        self.details = details or {}
        self.checked_at = datetime.utcnow()
    
    def is_healthy(self) -> bool:
        """Retorna True si el componente está healthy."""
        return self.status == self.HEALTHY
    
    def is_degraded(self) -> bool:
        """Retorna True si el componente está degraded."""
        return self.status == self.DEGRADED
    
    def is_unhealthy(self) -> bool:
        """Retorna True si el componente está unhealthy."""
        return self.status == self.UNHEALTHY
    
    def to_dict(self) -> dict:
        """Convierte el HealthStatus a diccionario."""
        return {
            "status": self.status,
            "message": self.message,
            "details": self.details,
            "checked_at": self.checked_at.isoformat()
        }


class ServiceHealth:
    """
    Aggregate Root que representa la salud general del servicio.
    
    Agrega múltiples checks de componentes individuales y proporciona
    una visión consolidada de la salud del servicio.
    
    Atributos:
        service_name (str): Nombre del servicio.
        version (str): Versión del servicio.
        checks (dict): Diccionario de HealthStatus de cada componente.
        checked_at (datetime): Marca de tiempo del check.
    """
    
    def __init__(self, service_name: str, version: str):
        """
        Inicializa ServiceHealth.
        
        Args:
            service_name: Nombre del servicio.
            version: Versión del servicio.
        """
        self.service_name = service_name
        self.version = version
        self.checks: dict = {}
        self.checked_at = datetime.utcnow()
    
    def add_check(self, component_name: str, status: HealthStatus) -> None:
        """
        Agrega un check de componente.
        
        Args:
            component_name: Nombre del componente.
            status: HealthStatus del componente.
        """
        self.checks[component_name] = status
    
    def overall_status(self) -> str:
        """
        Determina el estado general del servicio.
        
        Lógica:
        - Si hay alguno unhealthy → unhealthy
        - Si hay alguno degraded → degraded
        - Si todos healthy → healthy
        
        Returns:
            Estado general ('healthy', 'degraded', 'unhealthy').
        """
        if not self.checks:
            return HealthStatus.HEALTHY
        
        statuses = [check.status for check in self.checks.values()]
        
        if HealthStatus.UNHEALTHY in statuses:
            return HealthStatus.UNHEALTHY
        elif HealthStatus.DEGRADED in statuses:
            return HealthStatus.DEGRADED
        else:
            return HealthStatus.HEALTHY
    
    def is_ready(self) -> bool:
        """Retorna True si el servicio está listo (all healthy)."""
        return self.overall_status() == HealthStatus.HEALTHY
    
    def is_alive(self) -> bool:
        """Retorna True si el servicio está vivo (siempre true si responde)."""
        return True
    
    def to_dict(self) -> dict:
        """Convierte ServiceHealth a diccionario."""
        return {
            "service": self.service_name,
            "version": self.version,
            "status": self.overall_status(),
            "checks": {name: status.to_dict() for name, status in self.checks.items()},
            "checked_at": self.checked_at.isoformat()
        }
