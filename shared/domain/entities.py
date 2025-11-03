"""Entidades compartidas para todos los contextos."""
from dataclasses import dataclass, field
from datetime import datetime
from typing import Dict, Any, Optional


class AuditableEntity:
    """Entidad base con campos de auditoría para todas las entidades del dominio."""
    
    def __init__(self):
        self.created_at: datetime = datetime.utcnow()
        self.created_by: Optional[str] = None
        self.updated_at: datetime = datetime.utcnow()
        self.updated_by: Optional[str] = None
        self.deleted_at: Optional[datetime] = None
        self.deleted_by: Optional[str] = None
        self.is_deleted: bool = False
    
    def mark_created(self, user_id: Optional[str] = None) -> None:
        """Marca la entidad como creada."""
        self.created_at = datetime.utcnow()
        self.created_by = user_id
        self.updated_at = datetime.utcnow()
        self.updated_by = user_id
    
    def mark_updated(self, user_id: Optional[str] = None) -> None:
        """Marca la entidad como actualizada."""
        self.updated_at = datetime.utcnow()
        self.updated_by = user_id
    
    def mark_deleted(self, user_id: Optional[str] = None) -> None:
        """Marca la entidad como eliminada (soft delete)."""
        self.deleted_at = datetime.utcnow()
        self.deleted_by = user_id
        self.is_deleted = True
    
    def restore(self) -> None:
        """Restaura una entidad eliminada."""
        self.deleted_at = None
        self.deleted_by = None
        self.is_deleted = False
    
    def to_audit_dict(self) -> dict:
        """Retorna los datos de auditoría como diccionario."""
        return {
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "created_by": self.created_by,
            "updated_at": self.updated_at.isoformat() if self.updated_at else None,
            "updated_by": self.updated_by,
            "deleted_at": self.deleted_at.isoformat() if self.deleted_at else None,
            "deleted_by": self.deleted_by,
            "is_deleted": self.is_deleted,
        }


@dataclass
class ErrorResponse:
    """Respuesta de error estándar del dominio compartido."""
    
    error: str
    message: str
    code: str
    details: Dict[str, Any] = field(default=None)
    
    def to_dict(self) -> Dict[str, Any]:
        """Convierte la respuesta a diccionario."""
        result = {
            "error": self.error,
            "message": self.message,
            "code": self.code,
        }
        if self.details:
            result["details"] = self.details
        return result
