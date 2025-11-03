"""Configuración de Swagger/OpenAPI para la API de Detección de Incidencias."""

SWAGGER_CONFIG = {
    "title": "Servicio de Detección de Incidencias de Infraestructura",
    "version": "1.0.0",
    "description": """
    API REST para detección de incidencias de infraestructura usando Deep Learning (YOLO).
    
    ## Características Principales:
    - **Detection:** Análisis de imágenes para detectar baches, basura acumulada, semáforos malogrados, etc.
    - **Health:** Verificación de salud del servicio (Kubernetes ready/liveness probes)
    - **IAM:** Autenticación y gestión de clientes backend
    
    ## Arquitectura:
    - Hexagonal Architecture (Clean Code)
    - Domain-Driven Design (DDD)
    - Inyección de Dependencias
    - Auditoría de cambios automática
    
    ## Modelos de IA:
    - YOLO11 para detección de objetos
    - Almacenamiento en Cloudinary
    - Confianza configurable por categoría
    """,
    "termsOfService": "http://example.com/terms",
    "contact": {
        "name": "Smart Band Detection Service",
        "url": "http://localhost:5000",
        "email": "support@smartband.com",
    },
    "license": {
        "name": "MIT",
        "url": "https://opensource.org/licenses/MIT",
    },
    "servers": [
        {
            "url": "http://localhost:5000",
            "description": "Servidor Local (Desarrollo)",
        },
        {
            "url": "http://192.168.18.19:5000",
            "description": "Servidor en Red Local",
        },
    ],
}

SECURITY_SCHEMES = {
    "apiKey": {
        "type": "apiKey",
        "in": "header",
        "name": "X-API-Key",
        "description": "API Key para autenticación de cliente",
    }
}

# Documentación de tags
TAGS = {
    "health": {
        "name": "Health",
        "description": "Endpoints de verificación de salud del servicio",
    },
    "clients": {
        "name": "IAM - Clientes",
        "description": "Gestión de clientes backend y autenticación",
    },
    "detection": {
        "name": "Detection",
        "description": "Detección de incidencias de infraestructura",
    },
    "utils": {
        "name": "Utilidades",
        "description": "Endpoints de utilidad e información",
    },
}

# Modelos de respuesta para Swagger
RESPONSE_MODELS = {
    "health_response": {
        "type": "object",
        "properties": {
            "status": {"type": "string", "example": "healthy"},
            "timestamp": {"type": "string", "format": "date-time"},
            "checks": {
                "type": "object",
                "properties": {
                    "database": {"type": "string", "example": "ok"},
                    "yolo_model": {"type": "string", "example": "ok"},
                    "cloudinary": {"type": "string", "example": "ok"},
                }
            }
        }
    },
    "client_request": {
        "type": "object",
        "required": ["client_id", "name", "api_key"],
        "properties": {
            "client_id": {"type": "string", "example": "backend-service"},
            "name": {"type": "string", "example": "Mi Servicio Backend"},
            "api_key": {"type": "string", "example": "clave-secreta-123"}
        }
    },
    "client_response": {
        "type": "object",
        "properties": {
            "success": {"type": "boolean"},
            "message": {"type": "string"},
            "client": {
                "type": "object",
                "properties": {
                    "client_id": {"type": "string"},
                    "name": {"type": "string"},
                    "is_active": {"type": "boolean"},
                    "api_key": {"type": "string"}
                }
            }
        }
    },
    "detection_request": {
        "type": "object",
        "required": ["client_id", "uuid", "image_url"],
        "properties": {
            "client_id": {"type": "string", "example": "backend-service"},
            "uuid": {"type": "string", "format": "uuid", "example": "550e8400-e29b-41d4-a716-446655440000"},
            "image_url": {"type": "string", "format": "uri", "example": "https://example.com/image.jpg"},
            "latitude": {"type": "number", "example": -12.046374},
            "longitude": {"type": "number", "example": -77.042793}
        }
    },
    "detection_response": {
        "type": "object",
        "properties": {
            "success": {"type": "boolean"},
            "uuid": {"type": "string", "format": "uuid"},
            "status": {"type": "string", "enum": ["pending", "processing", "completed", "failed"]},
            "detections": {
                "type": "array",
                "items": {
                    "type": "object",
                    "properties": {
                        "class": {"type": "string", "example": "Pothole"},
                        "confidence": {"type": "number", "example": 0.95},
                        "bbox": {"type": "object", "properties": {
                            "x": {"type": "number"},
                            "y": {"type": "number"},
                            "width": {"type": "number"},
                            "height": {"type": "number"}
                        }}
                    }
                }
            },
            "image_url": {"type": "string", "format": "uri"},
            "created_at": {"type": "string", "format": "date-time"},
            "processed_at": {"type": "string", "format": "date-time"}
        }
    },
    "error_response": {
        "type": "object",
        "properties": {
            "error": {"type": "string"},
            "message": {"type": "string"},
            "code": {"type": "string"},
            "details": {"type": "object"}
        }
    }
}

