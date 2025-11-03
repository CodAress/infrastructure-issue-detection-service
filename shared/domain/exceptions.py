"""Excepciones de dominio compartidas para todos los contextos."""


class DomainException(Exception):
    """Excepción base del dominio."""
    
    def __init__(self, message: str, code: str = "DOMAIN_ERROR"):
        self.message = message
        self.code = code
        super().__init__(self.message)


class ValidationException(DomainException):
    """Excepción de validación."""
    
    def __init__(self, message: str):
        super().__init__(message, "VALIDATION_ERROR")


class ResourceNotFoundException(DomainException):
    """Excepción de recurso no encontrado."""
    
    def __init__(self, resource_type: str, resource_id: str):
        message = f"{resource_type} con ID '{resource_id}' no fue encontrado"
        super().__init__(message, "RESOURCE_NOT_FOUND")


class UnauthorizedException(DomainException):
    """Excepción de no autorizado."""
    
    def __init__(self, message: str = "No autorizado"):
        super().__init__(message, "UNAUTHORIZED")


class ForbiddenException(DomainException):
    """Excepción de acceso denegado."""
    
    def __init__(self, message: str = "Acceso denegado"):
        super().__init__(message, "FORBIDDEN")


class ConflictException(DomainException):
    """Excepción de conflicto."""
    
    def __init__(self, message: str):
        super().__init__(message, "CONFLICT")


class InternalServerException(DomainException):
    """Excepción de error interno del servidor."""
    
    def __init__(self, message: str = "Error interno del servidor"):
        super().__init__(message, "INTERNAL_SERVER_ERROR")
