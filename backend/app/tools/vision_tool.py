"""
LangChain Tool para análisis de imágenes académicas con Gemini Vision.

Este tool es compatible con LangGraph y puede ser usado por el agente
para procesar documentos académicos (oferta, mapa curricular, kárdex).
"""
import logging
from typing import Literal, Optional, Type

from langchain.tools import BaseTool
from pydantic import BaseModel, Field

from app.services.vision_service import (
    get_vision_service,
    VisionServiceError,
    DocType
)

logger = logging.getLogger(__name__)


class VisionToolInput(BaseModel):
    """Esquema de entrada para el VisionTool."""
    
    image_path: str = Field(
        description="Ruta absoluta al archivo de imagen a analizar"
    )
    doc_type: Literal["oferta", "mapa", "kardex"] = Field(
        description=(
            "Tipo de documento académico: "
            "'oferta' = Oferta académica con materias disponibles, "
            "'mapa' = Mapa curricular/plan de estudios, "
            "'kardex' = Historial académico del estudiante"
        )
    )
    use_pro: bool = Field(
        default=False,
        description=(
            "Si True, usa Gemini Pro (más preciso pero más lento). "
            "Usar solo para imágenes complejas o borrosas."
        )
    )


class VisionTool(BaseTool):
    """Herramienta para analizar imágenes de documentos académicos.
    
    Utiliza Gemini Vision API para extraer información estructurada
    de ofertas académicas, mapas curriculares y kárdex estudiantiles.
    
    Examples:
        >>> tool = VisionTool()
        >>> result = await tool._arun(
        ...     image_path="/uploads/oferta.jpg",
        ...     doc_type="oferta"
        ... )
        >>> print(result["materias"])
    """
    
    name: str = "vision_tool"
    description: str = """
    Analiza imágenes de documentos académicos y extrae información estructurada.
    
    Tipos de documentos soportados:
    - oferta: Oferta académica con materias, horarios, profesores y cupos
    - mapa: Mapa curricular con prerrequisitos y estructura del plan de estudios
    - kardex: Historial académico con calificaciones y avance del estudiante
    
    La imagen debe ser clara y legible. Formatos soportados: JPG, PNG, GIF, WEBP.
    Tamaño máximo: 10MB.
    
    Retorna un diccionario con la información extraída en formato estructurado.
    """
    args_schema: Type[BaseModel] = VisionToolInput
    
    def _run(
        self,
        image_path: str,
        doc_type: DocType,
        use_pro: bool = False
    ) -> dict:
        """Versión síncrona (no recomendada, usar _arun).
        
        Args:
            image_path: Ruta al archivo de imagen
            doc_type: Tipo de documento
            use_pro: Usar Gemini Pro
            
        Returns:
            Diccionario con datos extraídos o error
        """
        import asyncio
        
        try:
            loop = asyncio.get_event_loop()
        except RuntimeError:
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)
        
        return loop.run_until_complete(
            self._arun(image_path, doc_type, use_pro)
        )
    
    async def _arun(
        self,
        image_path: str,
        doc_type: DocType,
        use_pro: bool = False
    ) -> dict:
        """Analiza una imagen de documento académico.
        
        Args:
            image_path: Ruta absoluta al archivo de imagen
            doc_type: Tipo de documento ("oferta", "mapa", "kardex")
            use_pro: Si True, usa Gemini Pro para mayor precisión
            
        Returns:
            Diccionario con la información extraída:
            - Para "oferta": materias con NRC, horarios, profesores
            - Para "mapa": estructura de semestres y prerrequisitos
            - Para "kardex": historial con calificaciones y avance
            
            En caso de error, retorna:
            {"error": True, "message": "descripción del error"}
        """
        logger.info(f"VisionTool: Procesando {doc_type} desde {image_path}")
        
        try:
            service = get_vision_service()
            result = await service.analyze_from_path(
                image_path=image_path,
                doc_type=doc_type,
                use_pro=use_pro
            )
            
            # Log resumen según tipo
            if doc_type == "oferta" and "materias" in result:
                logger.info(f"Extraídas {len(result['materias'])} materias de oferta")
            elif doc_type == "mapa" and "semestres" in result:
                logger.info(f"Extraídos {len(result['semestres'])} semestres del mapa")
            elif doc_type == "kardex" and "periodos" in result:
                logger.info(f"Extraídos {len(result['periodos'])} periodos del kárdex")
            
            return result
            
        except VisionServiceError as e:
            logger.error(f"VisionTool error: {e}")
            return {
                "error": True,
                "message": str(e),
                "doc_type": doc_type
            }
        except Exception as e:
            logger.exception(f"VisionTool error inesperado: {e}")
            return {
                "error": True,
                "message": f"Error inesperado: {e}",
                "doc_type": doc_type
            }


# Instancia del tool para importar directamente
vision_tool = VisionTool()
