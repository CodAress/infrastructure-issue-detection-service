"""
Servicio de Detección de Incidencias de Infraestructura
Punto de entrada de la aplicación Flask principal
"""
from flask import Flask
from flasgger import Flasgger
import logging
import os

from health.interfaces.services import health_api, set_health_service
from health.application.services import HealthApplicationService
from iam.interfaces.services import iam_api, set_auth_service
from iam.application.services import AuthApplicationService
from detection.interfaces.services import detection_api, set_detection_service
from detection.application.services import DetectionApplicationService
from detection.infrastructure.services import YoloInferenceService, CloudinaryService
from shared.infrastructure.database import init_db
from shared.interfaces.error_handlers import register_error_handlers

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

app = Flask(__name__)

# Configurar Flasgger para documentación Swagger/OpenAPI (ANTES de blueprints)
swagger_template = {
    "swagger": "2.0",
    "info": {
        "title": "Infrastructure Detection Service API",
        "description": "API para detección de incidencias de infraestructura usando YOLO",
        "version": "1.0.0",
        "contact": {
            "name": "API Support",
            "url": "https://github.com/CodAress/infrastructure-issue-detection-service"
        }
    },
    # No especificar 'host' para que Swagger use el host actual (localhost o DNS de producción)
    "basePath": "/",
    "schemes": ["http"],
    "securityDefinitions": {
        "X-API-Key": {
            "type": "apiKey",
            "name": "X-API-Key",
            "in": "header",
            "description": "API Key para autenticación de clientes"
        }
    }
}

swagger_config = Flasgger.DEFAULT_CONFIG.copy()
swagger_config.update({
    "headers": [],
    "specs_route": "/api/v1/docs",
    "static_url_path": "/flasgger_static",
    "swagger_ui": True,
    "specs": [
        {
            "endpoint": 'apispec',
            "route": '/api/v1/apispec.json',
        }
    ]
})

swagger = Flasgger(app, template=swagger_template, config=swagger_config)

# Registrar blueprints DESPUÉS de Flasgger
app.register_blueprint(health_api)
app.register_blueprint(iam_api)
app.register_blueprint(detection_api)

# Registrar los manejadores de errores centralizados
register_error_handlers(app)


def initialize_health_service():
    """
    Inicializa los servicios de Health con inyección de dependencias.
    
    Crea:
    1. HealthApplicationService - Orquesta verificaciones de salud
    2. Inyecta en la capa de interfaces
    """
    try:
        logger.info("Inicializando servicios de Health...")
        
        health_app_service = HealthApplicationService()
        
        logger.info("  📡 Registrando en capa de interfaces...")
        set_health_service(health_app_service)
        
        logger.info("✅ Servicios de Health inicializados correctamente")
        
    except Exception as e:
        logger.error(f"❌ Error inicializando servicios de Health: {e}")
        raise


def initialize_iam_service():
    """
    Inicializa los servicios de IAM con inyección de dependencias.
    
    Crea:
    1. AuthApplicationService - Orquesta autenticación y gestión de clientes
    2. Inyecta en la capa de interfaces
    3. Auto-registra cliente backend principal desde .env
    """
    try:
        logger.info("Inicializando servicios de IAM...")
        
        auth_app_service = AuthApplicationService()
        
        logger.info("  📡 Registrando en capa de interfaces...")
        set_auth_service(auth_app_service)
        
        # Auto-registrar cliente backend principal desde variables de entorno
        backend_client_id = os.getenv('BACKEND_CLIENT_ID')
        backend_api_key = os.getenv('BACKEND_API_KEY')
        backend_client_name = os.getenv('BACKEND_CLIENT_NAME', 'Backend Principal')
        
        if backend_client_id and backend_api_key:
            logger.info("  🔑 Inicializando cliente backend principal desde .env...")
            try:
                client = auth_app_service.get_or_create_backend_client(
                    client_id=backend_client_id,
                    api_key=backend_api_key,
                    name=backend_client_name
                )
                logger.info(f"  ✅ Cliente backend '{client.client_id}' inicializado correctamente")
            except Exception as e:
                logger.error(f"  ❌ Error inicializando cliente backend: {e}")
                raise
        else:
            logger.warning(
                "  ⚠️  BACKEND_CLIENT_ID o BACKEND_API_KEY no configurados en .env\n"
                "     El backend principal debe configurar estas variables para conectarse."
            )
        
        logger.info("✅ Servicios de IAM inicializados correctamente")
        
    except Exception as e:
        logger.error(f"❌ Error inicializando servicios de IAM: {e}")
        raise


def initialize_detection_service():
    """
    Inicializa los servicios de Detection con inyección de dependencias.
    
    Crea:
    1. YoloInferenceService - Carga modelo best.pt
    2. CloudinaryService - Configura credenciales
    3. DetectionApplicationService - Orquesta todo
    4. Inyecta en la capa de interfaces
    """
    try:
        logger.info("Inicializando servicios de Detection...")
        
        # Obtener configuración desde variables de entorno
        model_path = os.getenv('YOLO_MODEL_PATH', './models/best.pt')
        conf_threshold = float(os.getenv('YOLO_CONF_THRESHOLD', 0.30))
        
        cloudinary_cloud_name = os.getenv('CLOUDINARY_CLOUD_NAME')
        cloudinary_api_key = os.getenv('CLOUDINARY_API_KEY')
        cloudinary_api_secret = os.getenv('CLOUDINARY_API_SECRET')
        
        # Validar configuración requerida
        if not cloudinary_cloud_name or not cloudinary_api_key or not cloudinary_api_secret:
            raise ValueError(
                "Credenciales Cloudinary no configuradas. "
                "Establecer: CLOUDINARY_CLOUD_NAME, CLOUDINARY_API_KEY, CLOUDINARY_API_SECRET"
            )
        
        # Crear servicios de infraestructura
        logger.info(f"  📁 Cargando modelo YOLO desde: {model_path}")
        yolo_service = YoloInferenceService(
            model_path=model_path,
            conf_threshold=conf_threshold
        )
        logger.info(f"  ☁️  Configurando Cloudinary: {cloudinary_cloud_name}")
        cloudinary_service = CloudinaryService(
            cloud_name=cloudinary_cloud_name,
            api_key=cloudinary_api_key,
            api_secret=cloudinary_api_secret
        )
        
        # Crear servicio de aplicación
        logger.info("  🔗 Inyectando servicios en DetectionApplicationService...")
        detection_app_service = DetectionApplicationService(
            yolo_service=yolo_service,
            cloudinary_service=cloudinary_service
        )
        
        # Inyectar en la capa de interfaces
        logger.info("  📡 Registrando en capa de interfaces...")
        set_detection_service(detection_app_service)
        
        logger.info("✅ Servicios de Detection inicializados correctamente")
        
    except FileNotFoundError as e:
        logger.error(f"❌ Modelo YOLO no encontrado: {e}")
        raise
    except Exception as e:
        logger.error(f"❌ Error inicializando servicios de Detection: {e}")
        raise


@app.route('/api/v1/swagger-info')
def swagger_info():
    """Información sobre Swagger y documentación."""
    return {
        'message': 'Bienvenido al Servicio de Detección de Incidencias',
        'version': '1.0.0',
        'swagger_docs': '/api/v1/docs',
        'swagger_json': '/api/v1/apispec.json'
    }, 200


@app.route('/api/v1/info')
def about_service():
    """Punto final de información del servicio."""
    return {
        'service': 'Servicio de Detección de Incidencias de Infraestructura',
        'version': '1.0.0',
        'description': 'Servicio de Aprendizaje Profundo para detectar incidencias de infraestructura (baches, etc.)',
        'database': 'SQLite para almacenar consultas de análisis y resultados',
        'endpoints': {
            'documentation': 'GET /api/v1/docs (Swagger UI)',
            'swagger_json': 'GET /api/v1/apispec.json',
            'swagger_info': 'GET /api/v1/swagger-info',
            'info': 'GET /api/v1/info',
            'health': 'GET /api/v1/health',
            'health_readiness': 'GET /api/v1/health/readiness (Kubernetes probe)',
            'health_liveness': 'GET /api/v1/health/liveness (Kubernetes probe)',
            'health_components': 'GET /api/v1/health/components/{name}',
            'health_diagnostics': 'POST /api/v1/health/diagnostics',
            'clients_verify': 'GET /api/v1/clients/verify',
            'clients_get': 'GET /api/v1/clients/{client_id}',
            'detection_create': 'POST /api/v1/detecciones',
            'detection_result': 'GET /api/v1/detecciones/{uuid}',
            'detection_list': 'GET /api/v1/detecciones',
            'detection_batch': 'POST /api/v1/detecciones/_batch/procesar'
        }
    }, 200


if __name__ == '__main__':
    # Cargar variables de entorno desde .env si está presente
    from dotenv import load_dotenv
    load_dotenv()
    
    # Inicializar base de datos
    try:
        logger.info("Inicializando base de datos...")
        init_db()
        logger.info("✅ Base de datos inicializada exitosamente")
    except Exception as e:
        logger.error(f"❌ Error al inicializar base de datos: {str(e)}")
        raise
    
    # Inicializar servicios de Health
    try:
        initialize_health_service()
    except Exception as e:
        logger.error(f"❌ Fallo inicializando servicios de Health")
        raise
    
    # Inicializar servicios de IAM
    try:
        initialize_iam_service()
    except Exception as e:
        logger.error(f"❌ Fallo inicializando servicios de IAM")
        raise
    
    # Inicializar servicios de Detection
    try:
        initialize_detection_service()
    except Exception as e:
        logger.error(f"❌ Fallo inicializando servicios de Detection")
        raise
    
    # Obtener configuración
    debug_mode = os.getenv('FLASK_DEBUG', 'False').lower() == 'true'
    host = os.getenv('FLASK_HOST', '0.0.0.0')
    port = int(os.getenv('FLASK_PORT', 5000))
    
    logger.info(f"Iniciando Servicio de Detección de Incidencias de Infraestructura")
    logger.info(f"Ejecutándose en {host}:{port} (Debug: {debug_mode})")
    
    app.run(host=host, port=port, debug=debug_mode)

