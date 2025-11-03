"""Repositorio para gestionar ConsultaAnalisis en el contexto de Detection."""
from typing import Optional
from datetime import datetime
from detection.domain.entities import ConsultaAnalisis, ResultadoDeteccion
from detection.infrastructure.models import ConsultaAnalisisModel, DetalleDeteccionModel
from shared.domain.exceptions import ResourceNotFoundException, ConflictException


class DetectionRepository:
    """
    Repositorio que gestiona la persistencia de ConsultaAnalisis.
    
    Maneja todas las operaciones CRUD y de consulta para análisis de detección.
    """
    
    @staticmethod
    def create(consulta: ConsultaAnalisis) -> ConsultaAnalisis:
        """
        Persiste una nueva consulta de análisis.
        
        Args:
            consulta: Entidad ConsultaAnalisis del dominio
            
        Returns:
            La misma entidad (para compatibilidad)
            
        Raises:
            ConflictException: Si la consulta ya existe
        """
        try:
            # Verificar que no exista
            if DetectionRepository.get_by_uuid(consulta.uuid_consulta):
                raise ConflictException(
                    f"Consulta con UUID '{consulta.uuid_consulta}' ya existe"
                )
            
            # Crear modelo ORM
            ConsultaAnalisisModel.create(
                uuid_consulta=consulta.uuid_consulta,
                url_imagen=consulta.url_imagen,
                client_id=consulta.client_id,
                estado=consulta.estado,
                created_at=consulta.created_at,
                updated_at=consulta.updated_at
            )
            
            return consulta
        
        except ConflictException:
            raise
        except Exception as e:
            raise ConflictException(f"Error creando consulta: {str(e)}")
    
    @staticmethod
    def get_by_uuid(uuid_consulta: str) -> Optional[ConsultaAnalisis]:
        """
        Obtiene una consulta por su UUID.
        
        Args:
            uuid_consulta: UUID único de la consulta
            
        Returns:
            Entidad ConsultaAnalisis o None si no existe
        """
        try:
            modelo = ConsultaAnalisisModel.get_by_id(uuid_consulta)
            
            # Reconstruir entidad del dominio
            consulta = ConsultaAnalisis(
                uuid_consulta=modelo.uuid_consulta,
                url_imagen=modelo.url_imagen,
                client_id=modelo.client_id
            )
            
            # Restaurar estado
            consulta.estado = modelo.estado
            consulta.created_at = modelo.created_at
            consulta.updated_at = modelo.updated_at
            
            # Si tiene resultado, reconstruir
            if modelo.categoria:
                resultado = ResultadoDeteccion(
                    categoria=modelo.categoria,
                    confianza=modelo.confianza,
                    url_resultado=modelo.url_resultado,
                    num_detecciones=modelo.num_detecciones
                )
                consulta.resultado = resultado
            
            if modelo.error_mensaje:
                consulta.error_mensaje = modelo.error_mensaje
            
            return consulta
        
        except ConsultaAnalisisModel.DoesNotExist:
            return None
    
    @staticmethod
    def update(consulta: ConsultaAnalisis) -> ConsultaAnalisis:
        """
        Actualiza una consulta existente.
        
        Args:
            consulta: Entidad ConsultaAnalisis del dominio
            
        Returns:
            La misma entidad
            
        Raises:
            ResourceNotFoundException: Si no existe
        """
        try:
            modelo = ConsultaAnalisisModel.get_by_id(consulta.uuid_consulta)
            
            # Actualizar campos
            modelo.estado = consulta.estado
            modelo.updated_at = datetime.utcnow()
            
            # Si tiene resultado, guardar
            if consulta.resultado:
                modelo.categoria = str(consulta.resultado.categoria)
                modelo.confianza = consulta.resultado.confianza
                modelo.url_resultado = consulta.resultado.url_resultado
                modelo.num_detecciones = consulta.resultado.num_detecciones
            
            if consulta.error_mensaje:
                modelo.error_mensaje = consulta.error_mensaje
            
            modelo.save()
            
            return consulta
        
        except ConsultaAnalisisModel.DoesNotExist:
            raise ResourceNotFoundException("ConsultaAnalisis", consulta.uuid_consulta)
    
    @staticmethod
    def get_by_client(client_id: str, skip: int = 0, limit: int = 10) -> list:
        """
        Obtiene todas las consultas de un cliente (paginadas).
        
        Args:
            client_id: ID del cliente
            skip: Número de registros a saltar
            limit: Máximo de registros
            
        Returns:
            Lista de entidades ConsultaAnalisis
        """
        modelos = (
            ConsultaAnalisisModel
            .select()
            .where(ConsultaAnalisisModel.client_id == client_id)
            .order_by(ConsultaAnalisisModel.created_at.desc())
            .offset(skip)
            .limit(limit)
        )
        
        consultas = []
        for modelo in modelos:
            consulta = ConsultaAnalisis(
                uuid_consulta=modelo.uuid_consulta,
                url_imagen=modelo.url_imagen,
                client_id=modelo.client_id
            )
            consulta.estado = modelo.estado
            consulta.created_at = modelo.created_at
            consulta.updated_at = modelo.updated_at
            
            if modelo.categoria:
                resultado = ResultadoDeteccion(
                    categoria=modelo.categoria,
                    confianza=modelo.confianza,
                    url_resultado=modelo.url_resultado,
                    num_detecciones=modelo.num_detecciones
                )
                consulta.resultado = resultado
            
            consultas.append(consulta)
        
        return consultas
    
    @staticmethod
    def count_by_client(client_id: str) -> int:
        """
        Cuenta total de consultas de un cliente.
        
        Args:
            client_id: ID del cliente
            
        Returns:
            Cantidad total de consultas
        """
        return (
            ConsultaAnalisisModel
            .select()
            .where(ConsultaAnalisisModel.client_id == client_id)
            .count()
        )
    
    @staticmethod
    def get_by_estado(estado: str) -> list:
        """
        Obtiene todas las consultas en un estado específico.
        Útil para procesar lotes de análisis pendientes.
        
        Args:
            estado: Estado a filtrar
            
        Returns:
            Lista de entidades ConsultaAnalisis
        """
        modelos = (
            ConsultaAnalisisModel
            .select()
            .where(ConsultaAnalisisModel.estado == estado)
            .order_by(ConsultaAnalisisModel.created_at.asc())
        )
        
        consultas = []
        for modelo in modelos:
            consulta = ConsultaAnalisis(
                uuid_consulta=modelo.uuid_consulta,
                url_imagen=modelo.url_imagen,
                client_id=modelo.client_id
            )
            consulta.estado = modelo.estado
            consulta.created_at = modelo.created_at
            consulta.updated_at = modelo.updated_at
            consultas.append(consulta)
        
        return consultas
    
    @staticmethod
    def save_detection_detail(uuid_consulta: str, 
                                   modelo_version: str,
                                   imgsz: int,
                                   umbral_confianza: float,
                                   clases_encontradas: str,
                                   confianzas_raw: Optional[str] = None,
                                   tiempo_inferencia_ms: int = 0) -> None:
        """
        Guarda detalles granulares de la detección para análisis posterior.
        
        Args:
            uuid_consulta: UUID de la consulta
            modelo_version: Versión del modelo (ej: best.pt)
            imgsz: Tamaño de imagen procesada
            umbral_confianza: Umbral usado
            clases_encontradas: JSON de clases
            confianzas_raw: JSON de valores de confianza
            tiempo_inferencia_ms: Tiempo de inferencia en ms
        """
        try:
            DetalleDeteccionModel.create(
                consulta_analisis=uuid_consulta,
                modelo_version=modelo_version,
                imgsz=imgsz,
                umbral_confianza=umbral_confianza,
                clases_encontradas=clases_encontradas,
                confianzas_raw=confianzas_raw,
                tiempo_inferencia_ms=tiempo_inferencia_ms
            )
        except Exception as e:
            # Log pero no falla - es información adicional
            import logging
            logger = logging.getLogger(__name__)
            logger.warning(f"No se guardaron detalles de detección: {e}")
