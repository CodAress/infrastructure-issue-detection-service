"""Modelos de infraestructura - Health Checkers para verificar componentes individuales."""
from abc import ABC, abstractmethod
from datetime import datetime
import logging
import time
import psutil

from health.domain.entities import HealthStatus
from health.domain.services import HealthCheckService

logger = logging.getLogger(__name__)


class HealthChecker(ABC):
    """Clase base abstracta para todos los health checkers."""
    
    @abstractmethod
    def check(self) -> HealthStatus:
        """Ejecuta el health check y retorna el estado."""
        pass
    
    def _measure_latency(self, func, *args, **kwargs) -> tuple:
        """Mide la latencia de ejecución de una función."""
        start = time.time()
        result = func(*args, **kwargs)
        latency_ms = (time.time() - start) * 1000
        return result, latency_ms


class DatabaseChecker(HealthChecker):
    """Checker para verificar la disponibilidad de la base de datos."""
    
    def check(self) -> HealthStatus:
        try:
            from shared.infrastructure.database import db
            
            def query():
                db.execute_sql('SELECT 1')
            
            result, latency = self._measure_latency(query)
            status = HealthCheckService.classify_database_latency(latency)
            
            return HealthStatus(
                status=status,
                message=f"Database latency: {latency:.2f}ms",
                details={
                    "latency_ms": round(latency, 2),
                    "timestamp": datetime.utcnow().isoformat()
                }
            )
        except Exception as e:
            logger.error(f"Database check failed: {str(e)}")
            return HealthStatus(
                status=HealthStatus.UNHEALTHY,
                message=f"Database check failed: {str(e)}",
                details={"error": str(e)}
            )


class IAMChecker(HealthChecker):
    """Checker para verificar que el contexto IAM esté funcional."""
    
    def check(self) -> HealthStatus:
        try:
            from iam.infrastructure.repositories import ClientRepository
            
            active_clients = ClientRepository.get_all_active()
            client_count = len(active_clients)
            
            if client_count == 0:
                return HealthStatus(
                    status=HealthStatus.DEGRADED,
                    message="No active clients found",
                    details={
                        "active_clients": client_count,
                        "timestamp": datetime.utcnow().isoformat()
                    }
                )
            
            return HealthStatus(
                status=HealthStatus.HEALTHY,
                message=f"IAM functional with {client_count} active clients",
                details={
                    "active_clients": client_count,
                    "timestamp": datetime.utcnow().isoformat()
                }
            )
        except Exception as e:
            logger.error(f"IAM check failed: {str(e)}")
            return HealthStatus(
                status=HealthStatus.UNHEALTHY,
                message=f"IAM check failed: {str(e)}",
                details={"error": str(e)}
            )


class MemoryChecker(HealthChecker):
    """Checker para verificar el uso de memoria del sistema."""
    
    def check(self) -> HealthStatus:
        try:
            memory = psutil.virtual_memory()
            percent = memory.percent
            status = HealthCheckService.classify_memory_usage(percent)
            
            return HealthStatus(
                status=status,
                message=f"Memory usage: {percent}%",
                details={
                    "memory_percent": round(percent, 2),
                    "memory_used_gb": round(memory.used / (1024**3), 2),
                    "memory_total_gb": round(memory.total / (1024**3), 2),
                    "timestamp": datetime.utcnow().isoformat()
                }
            )
        except Exception as e:
            logger.error(f"Memory check failed: {str(e)}")
            return HealthStatus(
                status=HealthStatus.UNHEALTHY,
                message=f"Memory check failed: {str(e)}",
                details={"error": str(e)}
            )


class DiskSpaceChecker(HealthChecker):
    """Checker para verificar el espacio en disco disponible."""
    
    def check(self) -> HealthStatus:
        try:
            disk = psutil.disk_usage('/')
            percent = disk.percent
            status = HealthCheckService.classify_disk_usage(percent)
            
            return HealthStatus(
                status=status,
                message=f"Disk usage: {percent}%",
                details={
                    "disk_percent": round(percent, 2),
                    "disk_used_gb": round(disk.used / (1024**3), 2),
                    "disk_total_gb": round(disk.total / (1024**3), 2),
                    "timestamp": datetime.utcnow().isoformat()
                }
            )
        except Exception as e:
            logger.error(f"Disk check failed: {str(e)}")
            return HealthStatus(
                status=HealthStatus.UNHEALTHY,
                message=f"Disk check failed: {str(e)}",
                details={"error": str(e)}
            )


class APIResponseChecker(HealthChecker):
    """Checker para verificar que la API está respondiendo."""
    
    def check(self) -> HealthStatus:
        try:
            from flask import current_app
            
            blueprints = list(current_app.blueprints.keys())
            
            if len(blueprints) == 0:
                return HealthStatus(
                    status=HealthStatus.UNHEALTHY,
                    message="No blueprints registered",
                    details={"blueprints": blueprints}
                )
            
            return HealthStatus(
                status=HealthStatus.HEALTHY,
                message=f"API responding with {len(blueprints)} blueprints",
                details={
                    "blueprints": blueprints,
                    "timestamp": datetime.utcnow().isoformat()
                }
            )
        except Exception as e:
            logger.error(f"API check failed: {str(e)}")
            return HealthStatus(
                status=HealthStatus.UNHEALTHY,
                message=f"API check failed: {str(e)}",
                details={"error": str(e)}
            )
