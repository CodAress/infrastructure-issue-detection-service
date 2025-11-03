"""Manejadores de errores Flask para la aplicación."""
from flask import Flask, jsonify
from shared.infrastructure.error_mapper import ErrorMapper
from shared.domain.exceptions import DomainException


def register_error_handlers(app: Flask) -> None:
    """Registra los manejadores de errores en la aplicación Flask."""
    
    @app.errorhandler(404)
    def handle_404(e):
        response, status_code = ErrorMapper.handle_not_found("Endpoint no encontrado")
        return jsonify(response), status_code
    
    @app.errorhandler(405)
    def handle_405(e):
        response, status_code = ErrorMapper.handle_method_not_allowed()
        return jsonify(response), status_code
    
    @app.errorhandler(DomainException)
    def handle_domain_exception(e):
        response, status_code = ErrorMapper.handle_exception(e)
        return jsonify(response), status_code
    
    @app.errorhandler(Exception)
    def handle_generic_exception(e):
        response, status_code = ErrorMapper.handle_exception(e)
        return jsonify(response), status_code
