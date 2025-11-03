"""
Application Layer for Detection BC - Service Orchestration

Capa de Aplicación para Detection BC - Orquestación de Servicios
"""
import logging
import json
import time
from typing import Optional, List, Tuple

from detection.domain.entities import ConsultaAnalisis, ResultadoDeteccion
from detection.domain.services import DetectionService
from detection.infrastructure.repositories import DetectionRepository
from detection.infrastructure.services import YoloInferenceService, CloudinaryService
from shared.domain.exceptions import ValidationException, ResourceNotFoundException

logger = logging.getLogger(__name__)


class DetectionApplicationService:
    """
    Servicio de aplicación que orquesta el análisis de imágenes.
    
    Flujo completo:
    1. Recibe solicitud con URL de imagen (desde backend principal)
    2. Backend principal genera UUID (no este servicio)
    3. Crea ConsultaAnalisis con ese UUID
    4. Descarga imagen desde URL
    5. Ejecuta inferencia YOLO
    6. Sube resultado anotado a Cloudinary
    7. Guarda en BD con resultado
    8. Retorna resultado al cliente
    
    Application Layer:
    - Orquesta lógica de dominio
    - Coordina servicios de infraestructura
    - Maneja flujos complejos
    """
    
    def __init__(self, yolo_service: YoloInferenceService, 
                 cloudinary_service: CloudinaryService):
        """
        Inicializa el servicio con inyección de dependencias.
        
        Args:
            yolo_service: Servicio de inferencia YOLO
            cloudinary_service: Servicio de almacenamiento en Cloudinary
        """
        self.yolo_service = yolo_service
        self.cloudinary_service = cloudinary_service
    
    def create_analysis_request(self, uuid_consulta: str, 
                               url_imagen: str, 
                               client_id: str) -> ConsultaAnalisis:
        """
        Crea una nueva solicitud de análisis.
        
        Nota: El UUID es generado y enviado por el backend principal,
        no por este servicio.
        
        Args:
            uuid_consulta: UUID generado por backend principal
            url_imagen: URL de la imagen a analizar
            client_id: ID del cliente que solicita
            
        Returns:
            Entidad ConsultaAnalisis creada
            
        Raises:
            ValidationException: Datos inválidos
            ConflictException: UUID ya existe
        """
        # Validar inputs
        if not uuid_consulta or not url_imagen or not client_id:
            raise ValidationException("uuid_consulta, url_imagen y client_id son requeridos")
        
        # Crear entidad del dominio
        consulta = ConsultaAnalisis(
            uuid_consulta=uuid_consulta,
            url_imagen=url_imagen,
            client_id=client_id
        )
        
        # Marcar como creada (inicializa campos de auditoría)
        consulta.mark_created(user_id=client_id)
        
        # Persistir en repositorio
        DetectionRepository.create(consulta)
        
        logger.info(f"✅ Solicitud de análisis creada: {uuid_consulta} (cliente: {client_id})")
        
        return consulta
    
    def execute_analysis(self, uuid_consulta: str) -> ConsultaAnalisis:
        """
        Ejecuta el análisis completo de una solicitud.
        
        FLUJO COMPLETO:
        1. Obtiene solicitud (estado: PENDIENTE)
        2. Marca PROCESANDO
        3. Descarga imagen desde URL
        4. Ejecuta inferencia YOLO
        5. Valida confianza contra umbral
        6. Si válida: sube imagen anotada a Cloudinary
        7. Crea ResultadoDeteccion
        8. Marca COMPLETADO con resultado
        9. Si error: marca ERROR con mensaje
        
        Args:
            uuid_consulta: UUID de la solicitud
            
        Returns:
            Entidad ConsultaAnalisis actualizada
            
        Raises:
            ResourceNotFoundException: Si no existe
            Exception: Cualquier error durante procesamiento
        """
        # Obtener solicitud
        consulta = DetectionRepository.get_by_uuid(uuid_consulta)
        if not consulta:
            raise ResourceNotFoundException("ConsultaAnalisis", uuid_consulta)
        
        try:
            # Marcar como procesando
            consulta.mark_processing()
            DetectionRepository.update(consulta)
            
            logger.info(f"🔄 Procesando análisis: {uuid_consulta}")
            
            # Descargar imagen
            logger.info(f"   📥 Descargando imagen: {consulta.url_imagen}")
            imagen_bgr = self.yolo_service.download_image_from_url(consulta.url_imagen)
            
            # Ejecutar inferencia
            logger.info(f"   🤖 Ejecutando YOLO inference...")
            inicio = time.time()
            yolo_result = self.yolo_service.infer(imagen_bgr)
            tiempo_ms = int((time.time() - inicio) * 1000)
            
            # Si no hay detecciones, marcar como completado
            if yolo_result['num_detecciones'] == 0:
                logger.info(f"   ✅ Sin incidencias detectadas")
                
                resultado = ResultadoDeteccion(
                    categoria="ninguna",
                    confianza=0.0,
                    url_resultado="",
                    num_detecciones=0
                )
                
                consulta.mark_completed(resultado)
                DetectionRepository.update(consulta)
                
                return consulta
            
            # Validar confianza con servicio de dominio
            categoria = yolo_result['categoria']
            confianza = yolo_result['confianza']
            
            if not DetectionService.validate_confidence(categoria, confianza):
                logger.warning(
                    f"   ⚠️  Confianza insuficiente: {categoria} ({confianza:.2%})"
                )
                
                resultado = ResultadoDeteccion(
                    categoria=categoria,
                    confianza=confianza,
                    url_resultado="",
                    num_detecciones=0
                )
                
                consulta.mark_completed(resultado)
                DetectionRepository.update(consulta)
                
                return consulta
            
            # Subir imagen anotada a Cloudinary
            logger.info(f"   ☁️  Subiendo a Cloudinary...")
            imagen_anotada = yolo_result['imagen_anotada']
            url_resultado = self.cloudinary_service.upload_annotated_image(
                imagen_anotada,
                uuid_consulta
            )
            
            # Crear resultado del dominio
            resultado = ResultadoDeteccion(
                categoria=categoria,
                confianza=confianza,
                url_resultado=url_resultado,
                num_detecciones=yolo_result['num_detecciones'],
                detalles={
                    "severidad": DetectionService.classify_severity(confianza),
                    "etiquetas": DetectionService.generate_result_tags(
                        categoria,
                        yolo_result['num_detecciones']
                    ),
                    "tiempo_inferencia_ms": tiempo_ms
                }
            )
            
            # Marcar como completado
            consulta.mark_completed(resultado)
            DetectionRepository.update(consulta)
            
            # Guardar detalles (opcional, no falla si hay error)
            DetectionRepository.save_detection_detail(
                uuid_consulta=uuid_consulta,
                modelo_version="best.pt",
                imgsz=640,
                umbral_confianza=self.yolo_service.conf_threshold,
                clases_encontradas=json.dumps(yolo_result['detalles'].get('clases_encontradas', [])),
                confianzas_raw=json.dumps(yolo_result['detalles'].get('confianzas', [])),
                tiempo_inferencia_ms=tiempo_ms
            )
            
            logger.info(f"   ✅ Análisis completado: {categoria} ({confianza:.2%})")
            
            return consulta
        
        except Exception as e:
            logger.error(f"❌ Error en análisis: {e}")
            consulta.mark_error(str(e))
            DetectionRepository.update(consulta)
            return consulta
    
    def get_analysis_request(self, uuid_consulta: str) -> Optional[ConsultaAnalisis]:
        """
        Obtiene una solicitud de análisis por UUID.
        
        Args:
            uuid_consulta: UUID de la solicitud
            
        Returns:
            Entidad ConsultaAnalisis o None
        """
        return DetectionRepository.get_by_uuid(uuid_consulta)
    
    def list_client_analysis_requests(self, client_id: str, 
                                     skip: int = 0, 
                                     limit: int = 10) -> Tuple[List[ConsultaAnalisis], int]:
        """
        Lista todas las solicitudes de un cliente con paginación.
        
        Args:
            client_id: ID del cliente
            skip: Registros a saltar
            limit: Máximo de registros a retornar
            
        Returns:
            Tupla (lista de solicitudes, total de registros)
        """
        consultas = DetectionRepository.get_by_client(client_id, skip, limit)
        total = DetectionRepository.count_by_client(client_id)
        return consultas, total
    
    def get_pending_analysis_requests(self) -> List[ConsultaAnalisis]:
        """
        Obtiene todas las solicitudes con estado PENDIENTE.
        
        Usado por procesador batch para encontrar análisis a procesar.
        
        Returns:
            Lista de ConsultaAnalisis con estado PENDIENTE
        """
        return DetectionRepository.get_by_estado(ConsultaAnalisis.PENDIENTE)
