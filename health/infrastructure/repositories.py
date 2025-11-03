"""Repositorio de Health - Orquesta todos los health checkers."""
from typing import Dict, Optional

from health.domain.entities import HealthStatus, ServiceHealth
from health.infrastructure.models import (
    HealthChecker,
    DatabaseChecker,
    IAMChecker,
    MemoryChecker,
    DiskSpaceChecker,
    APIResponseChecker
)


class HealthRepository:
    """
    Repositorio que orquesta múltiples health checkers.
    
    Ejecuta todos los checks registrados y agrega los resultados
    en un reporte de salud del servicio.
    """
    
    def __init__(self):
        """Inicializa el repositorio con los checkers por defecto."""
        self.checkers: Dict[str, HealthChecker] = {}
        
        # Registrar checkers por defecto
        self.add_checker("database", DatabaseChecker())
        self.add_checker("iam", IAMChecker())
        self.add_checker("memory", MemoryChecker())
        self.add_checker("disk", DiskSpaceChecker())
        self.add_checker("api", APIResponseChecker())
    
    def add_checker(self, name: str, checker: HealthChecker) -> None:
        """Agrega un nuevo health checker."""
        if not isinstance(checker, HealthChecker):
            raise ValueError(f"Checker debe ser instancia de HealthChecker")
        self.checkers[name] = checker
    
    def remove_checker(self, name: str) -> bool:
        """Remueve un health checker."""
        if name in self.checkers:
            del self.checkers[name]
            return True
        return False
    
    def get_checker(self, name: str) -> Optional[HealthChecker]:
        """Obtiene un checker específico por nombre."""
        return self.checkers.get(name)
    
    def get_full_health(self, service_name: str, version: str) -> ServiceHealth:
        """Ejecuta todos los checks y retorna reporte completo."""
        health = ServiceHealth(service_name, version)
        
        for name, checker in self.checkers.items():
            try:
                status = checker.check()
                health.add_check(name, status)
            except Exception as e:
                error_status = HealthStatus(
                    status=HealthStatus.UNHEALTHY,
                    message=f"Check '{name}' falló: {str(e)}",
                    details={"error": str(e)}
                )
                health.add_check(name, error_status)
        
        return health
    
    def get_quick_health(self, service_name: str, version: str, 
                         check_names: list = None) -> ServiceHealth:
        """Ejecuta checks específicos para readiness probe rápido."""
        if check_names is None:
            check_names = ["database", "iam"]
        
        health = ServiceHealth(service_name, version)
        
        for name in check_names:
            checker = self.checkers.get(name)
            if checker is None:
                continue
            
            try:
                status = checker.check()
                health.add_check(name, status)
            except Exception as e:
                error_status = HealthStatus(
                    status=HealthStatus.UNHEALTHY,
                    message=f"Check '{name}' falló: {str(e)}",
                    details={"error": str(e)}
                )
                health.add_check(name, error_status)
        
        return health
