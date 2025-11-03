"""Servicio de aplicación para Health - Orquesta domain + infrastructure."""
from health.domain.entities import ServiceHealth
from health.infrastructure.repositories import HealthRepository


class HealthApplicationService:
    """
    Servicio de aplicación que orquesta la ejecución de health checks.
    
    Actúa como intermediario entre los interfaces (HTTP) y la capa
    de infraestructura/dominio.
    """
    
    def __init__(self, service_name: str = "infrastructure-issue-detection-service",
                 version: str = "1.0.0"):
        """
        Inicializa el servicio de aplicación.
        
        Args:
            service_name: Nombre del servicio.
            version: Versión del servicio.
        """
        self.service_name = service_name
        self.version = version
        self.repository = HealthRepository()
    
    def get_health(self) -> dict:
        """
        Obtiene el estado de salud completo del servicio.
        
        Ejecuta todos los health checks.
        
        Returns:
            Diccionario con la salud del servicio.
        """
        health = self.repository.get_full_health(self.service_name, self.version)
        return health.to_dict()
    
    def get_quick_health(self, check_names: list = None) -> dict:
        """
        Obtiene estado de salud rápido (solo checks especificados).
        
        Args:
            check_names: Lista de nombres de checks a ejecutar.
            
        Returns:
            Diccionario con la salud del servicio.
        """
        health = self.repository.get_quick_health(
            self.service_name,
            self.version,
            check_names
        )
        return health.to_dict()
    
    def is_healthy(self) -> bool:
        """Verifica si el servicio está healthy."""
        health = self.repository.get_full_health(self.service_name, self.version)
        return health.is_ready()
    
    def is_ready(self) -> bool:
        """Verifica si el servicio está listo para recibir tráfico."""
        health = self.repository.get_quick_health(
            self.service_name,
            self.version,
            ["database", "iam"]
        )
        return health.is_ready()
    
    def is_alive(self) -> bool:
        """Verifica si el servicio está vivo (Kubernetes liveness probe)."""
        return True
    
    def get_component_health(self, component_name: str) -> dict:
        """
        Obtiene el estado de un componente específico.
        
        Args:
            component_name: Nombre del componente.
            
        Returns:
            Diccionario con el estado del componente o None.
        """
        checker = self.repository.get_checker(component_name)
        if checker is None:
            return None
        
        status = checker.check()
        return status.to_dict()
    
    def register_custom_checker(self, name: str, checker) -> None:
        """Registra un custom health checker."""
        self.repository.add_checker(name, checker)
