"""Mapeador centralizado de excepciones a respuestas HTTP."""
from flask import jsonify
from typing import Tuple, Dict, Any
from shared.domain.exceptions import (
    DomainException,
    ValidationException,
    ResourceNotFoundException,
    UnauthorizedException,
    ForbiddenException,
    ConflictException,
    InternalServerException,
)


class ErrorMapper:
    """Mapea excepciones de dominio a respuestas HTTP."""
    
    @staticmethod
    def handle_exception(exception: Exception, context: str = "") -> Tuple[Dict[str, Any], int]:
        """
        Maneja excepciones y retorna respuesta HTTP.
        
        Args:
            exception: Excepción a manejar
            context: Contexto adicional para el log
            
        Returns:
            Tupla de (response_dict, status_code)
        """
        if isinstance(exception, ValidationException):
            return ErrorMapper._validation_error(exception)
        elif isinstance(exception, UnauthorizedException):
            return ErrorMapper._unauthorized_error(exception)
        elif isinstance(exception, ForbiddenException):
            return ErrorMapper._forbidden_error(exception)
        elif isinstance(exception, ResourceNotFoundException):
            return ErrorMapper._not_found_error(exception)
        elif isinstance(exception, ConflictException):
            return ErrorMapper._conflict_error(exception)
        elif isinstance(exception, InternalServerException):
            return ErrorMapper._internal_error(exception)
        elif isinstance(exception, DomainException):
            return ErrorMapper._domain_error(exception)
        else:
            return ErrorMapper._generic_error(exception)
    
    @staticmethod
    def handle_not_found(message: str = "Recurso no encontrado") -> Tuple[Dict[str, Any], int]:
        """Maneja errores 404."""
        return {
            "error": "Not Found",
            "message": message,
            "code": "NOT_FOUND",
        }, 404
    
    @staticmethod
    def handle_method_not_allowed(method: str = "", path: str = "") -> Tuple[Dict[str, Any], int]:
        """Maneja errores 405."""
        message = f"Método {method} no permitido en {path}" if method and path else "Método no permitido"
        return {
            "error": "Method Not Allowed",
            "message": message,
            "code": "METHOD_NOT_ALLOWED",
        }, 405
    
    @staticmethod
    def _validation_error(exception: ValidationException) -> Tuple[Dict[str, Any], int]:
        """Error de validación (400)."""
        return {
            "error": "Validation Error",
            "message": exception.message,
            "code": exception.code,
        }, 400
    
    @staticmethod
    def _unauthorized_error(exception: UnauthorizedException) -> Tuple[Dict[str, Any], int]:
        """Error de no autorizado (401)."""
        return {
            "error": "Unauthorized",
            "message": exception.message,
            "code": exception.code,
        }, 401
    
    @staticmethod
    def _forbidden_error(exception: ForbiddenException) -> Tuple[Dict[str, Any], int]:
        """Error de acceso denegado (403)."""
        return {
            "error": "Forbidden",
            "message": exception.message,
            "code": exception.code,
        }, 403
    
    @staticmethod
    def _not_found_error(exception: ResourceNotFoundException) -> Tuple[Dict[str, Any], int]:
        """Error de recurso no encontrado (404)."""
        return {
            "error": "Not Found",
            "message": exception.message,
            "code": exception.code,
        }, 404
    
    @staticmethod
    def _conflict_error(exception: ConflictException) -> Tuple[Dict[str, Any], int]:
        """Error de conflicto (409)."""
        return {
            "error": "Conflict",
            "message": exception.message,
            "code": exception.code,
        }, 409
    
    @staticmethod
    def _internal_error(exception: InternalServerException) -> Tuple[Dict[str, Any], int]:
        """Error interno del servidor (500)."""
        return {
            "error": "Internal Server Error",
            "message": exception.message,
            "code": exception.code,
        }, 500
    
    @staticmethod
    def _domain_error(exception: DomainException) -> Tuple[Dict[str, Any], int]:
        """Error de dominio genérico (500)."""
        return {
            "error": "Domain Error",
            "message": exception.message,
            "code": exception.code,
        }, 500
    
    @staticmethod
    def _generic_error(exception: Exception) -> Tuple[Dict[str, Any], int]:
        """Error genérico no identificado (500)."""
        return {
            "error": "Internal Server Error",
            "message": str(exception),
            "code": "INTERNAL_SERVER_ERROR",
        }, 500
