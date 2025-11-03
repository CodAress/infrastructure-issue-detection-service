"""Servicios de infraestructura: Inference de YOLO + Almacenamiento en Cloudinary."""
import os
import cv2
import numpy as np
from typing import Tuple, Dict, Optional
from urllib.request import urlopen
from io import BytesIO
from PIL import Image
import cloudinary
import cloudinary.uploader
from ultralytics import YOLO
import logging

logger = logging.getLogger(__name__)


class YoloInferenceService:
    """
    Servicio de inferencia YOLO para detección de incidencias.
    
    Responsabilidades:
    - Cargar modelo YOLO (best.pt)
    - Ejecutar inferencia en imágenes
    - Procesar resultados del modelo
    """
    
    # Mapeo de categorías YOLO (inglés) a categorías del dominio (español)
    CATEGORY_MAP = {
        "Pothole": "bache",
        "pothole": "bache",
        "Garbage": "basura_acumulada",
        "garbage": "basura_acumulada",
        "TrafficLight": "semaforo_malogrado",
        "trafficlight": "semaforo_malogrado",
        "FallenPole": "poste_caido",
        "fallenpole": "poste_caido",
        # Mapeo directo (si el modelo ya devuelve en español)
        "bache": "bache",
        "basura_acumulada": "basura_acumulada",
        "semaforo_malogrado": "semaforo_malogrado",
        "poste_caido": "poste_caido"
    }
    
    def __init__(self, model_path: str, conf_threshold: float = 0.30):
        """
        Inicializa el servicio con el modelo YOLO.
        
        Args:
            model_path: Ruta al archivo best.pt
            conf_threshold: Umbral de confianza mínimo (default: 0.30)
        """
        if not os.path.exists(model_path):
            raise FileNotFoundError(f"Modelo YOLO no encontrado: {model_path}")
        
        self.model_path = model_path
        self.conf_threshold = conf_threshold
        
        try:
            self.modelo = YOLO(model_path)
            logger.info(f"✅ Modelo YOLO cargado: {model_path}")
            logger.info(f"   Clases: {self.modelo.names}")
            logger.info(f"   Umbral: {conf_threshold}")
        except Exception as e:
            logger.error(f"❌ Error cargando modelo YOLO: {e}")
            raise
    
    def download_image_from_url(self, url: str) -> np.ndarray:
        """
        Descarga imagen desde URL y la convierte a numpy array.
        
        Args:
            url: URL de la imagen
            
        Returns:
            Imagen como numpy array en formato OpenCV (BGR)
        """
        try:
            response = urlopen(url, timeout=10)
            image_data = np.asarray(bytearray(response.read()), dtype=np.uint8)
            image_bgr = cv2.imdecode(image_data, cv2.IMREAD_COLOR)
            
            if image_bgr is None:
                raise ValueError("No se pudo decodificar la imagen")
            
            return image_bgr
        
        except Exception as e:
            logger.error(f"❌ Error descargando imagen: {e}")
            raise
    
    def infer(self, imagen: np.ndarray) -> Dict:
        """
        Ejecuta inferencia YOLO en la imagen.
        
        Args:
            imagen: Imagen como numpy array (OpenCV format BGR)
            
        Returns:
            Dict con:
            - categoria: Clase detectada
            - confianza: Confianza máxima
            - num_detecciones: Cantidad de detecciones
            - imagen_anotada: Imagen con anotaciones (numpy array)
            - detalles: Info adicional
        """
        try:
            # Ejecutar predicción
            results = self.modelo.predict(
                source=imagen,
                imgsz=640,
                conf=self.conf_threshold,
                verbose=False
            )
            
            result = results[0]
            boxes = result.boxes
            num_detecciones = len(boxes)
            
            # Obtener imagen anotada
            imagen_anotada = result.plot()
            
            # Procesar detecciones
            if num_detecciones > 0:
                # Obtener clase y confianza máxima
                confianzas = boxes.conf.cpu().numpy()
                clases = boxes.cls.cpu().numpy().astype(int)
                
                clase_max_conf_idx = np.argmax(confianzas)
                clase_detectada = clases[clase_max_conf_idx]
                confianza_maxima = confianzas[clase_max_conf_idx]
                categoria_yolo = self.modelo.names[clase_detectada]
                
                # Traducir categoría de inglés a español usando el mapeo
                categoria = self.CATEGORY_MAP.get(categoria_yolo, categoria_yolo)
                
                logger.info(f"   🏷️  Categoría YOLO: '{categoria_yolo}' → Mapeada: '{categoria}'")
                
                return {
                    "categoria": categoria,
                    "confianza": float(confianza_maxima),
                    "num_detecciones": num_detecciones,
                    "imagen_anotada": imagen_anotada,
                    "detalles": {
                        "modelo": os.path.basename(self.model_path),
                        "imgsz": 640,
                        "umbral_conf": self.conf_threshold,
                        "clases_encontradas": [
                            self.modelo.names[int(cls)] 
                            for cls in np.unique(clases)
                        ],
                        "confianzas": confianzas.tolist()
                    }
                }
            else:
                return {
                    "categoria": None,
                    "confianza": 0.0,
                    "num_detecciones": 0,
                    "imagen_anotada": imagen_anotada,
                    "detalles": {
                        "modelo": os.path.basename(self.model_path),
                        "mensaje": "No se detectaron incidencias",
                        "umbral_conf": self.conf_threshold
                    }
                }
        
        except Exception as e:
            logger.error(f"❌ Error en inferencia YOLO: {e}")
            raise


class CloudinaryService:
    """
    Servicio de integración con Cloudinary para almacenar imágenes.
    
    Responsabilidades:
    - Configurar Cloudinary
    - Subir imagen anotada
    - Retornar URL público
    """
    
    def __init__(self, cloud_name: str, api_key: str, api_secret: str):
        """
        Inicializa Cloudinary con credenciales.
        
        Args:
            cloud_name: Nombre de la cuenta Cloudinary
            api_key: API Key
            api_secret: API Secret
        """
        self.cloud_name = cloud_name
        
        cloudinary.config(
            cloud_name=cloud_name,
            api_key=api_key,
            api_secret=api_secret
        )
        
        logger.info(f"✅ Cloudinary configurado: {cloud_name}")
    
    def upload_annotated_image(self, imagen_bgr: np.ndarray, 
                             public_id: str) -> str:
        """
        Sube imagen anotada a Cloudinary.
        
        Args:
            imagen_bgr: Imagen en formato OpenCV (BGR)
            public_id: ID público para la imagen (ej: uuid_consulta)
            
        Returns:
            URL pública de la imagen en Cloudinary
        """
        try:
            # Convertir BGR a RGB para PIL
            imagen_rgb = cv2.cvtColor(imagen_bgr, cv2.COLOR_BGR2RGB)
            
            # Convertir a PIL Image
            pil_image = Image.fromarray(imagen_rgb)
            
            # Guardar en memoria
            buffer = BytesIO()
            pil_image.save(buffer, format='PNG')
            buffer.seek(0)
            
            # Subir a Cloudinary
            resultado = cloudinary.uploader.upload(
                buffer,
                public_id=public_id,  # Solo el UUID, sin folder
                folder="detecciones",  # Folder donde se guardará
                resource_type="image",
                overwrite=True,
                format="png"
            )
            
            url_publica = resultado['secure_url']
            logger.info(f"✅ Imagen subida a Cloudinary: {url_publica}")
            
            return url_publica
        
        except Exception as e:
            logger.error(f"❌ Error subiendo a Cloudinary: {e}")
            raise
    
    def generate_optimized_url(self, public_id: str, 
                               width: int = 800, 
                               quality: str = "auto") -> str:
        """
        Genera URL optimizada de Cloudinary con transformaciones.
        
        Args:
            public_id: ID público de la imagen
            width: Ancho de la imagen
            quality: Calidad de compresión
            
        Returns:
            URL optimizada
        """
        from cloudinary.utils import cloudinary_url
        
        url, _ = cloudinary_url(
            f"detecciones/{public_id}",
            width=width,
            crop="fill",
            quality=quality,
            fetch_format="auto"
        )
        
        return url
