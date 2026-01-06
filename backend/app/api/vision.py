"""
API endpoints para el servicio de Vision (análisis de imágenes y PDFs).

Permite a los estudiantes subir imágenes o PDFs de:
- Oferta académica
- Mapa curricular
- Kárdex

Y obtener datos estructurados extraídos con Gemini Vision API.
"""
import logging
import os
import uuid
from typing import Literal

from fastapi import APIRouter, Depends, File, Form, HTTPException, UploadFile, status

from app.core.dependencies import get_current_user
from app.models.estudiante import Estudiante
from app.schemas.vision import VisionAnalyzeResponse
from app.services.vision_service import (
    get_vision_service,
    ImageValidationError,
    GeminiAPIError
)

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/vision", tags=["Vision AI"])

# Directorio para guardar imágenes temporales
UPLOAD_DIR = "/uploads"

# MIME types soportados
SUPPORTED_IMAGE_TYPES = {"image/jpeg", "image/png", "image/gif", "image/webp"}
SUPPORTED_PDF_TYPES = {"application/pdf"}
SUPPORTED_TYPES = SUPPORTED_IMAGE_TYPES | SUPPORTED_PDF_TYPES


def is_pdf(content_type: str) -> bool:
    """Verifica si el archivo es un PDF."""
    return content_type in SUPPORTED_PDF_TYPES


@router.post(
    "/analyze",
    response_model=VisionAnalyzeResponse,
    summary="Analizar imagen o PDF de documento académico",
    description="""
    Sube una imagen o PDF de un documento académico y obtén datos estructurados.
    
    **Tipos de documento soportados:**
    - `oferta`: Oferta académica con materias, horarios y cupos
    - `mapa`: Mapa curricular con prerrequisitos
    - `kardex`: Historial académico con calificaciones
    
    **Formatos soportados:** 
    - Imágenes: JPG, PNG, GIF, WEBP (máx 10MB)
    - PDFs: hasta 10 páginas (máx 20MB)
    
    **Respuesta:** JSON estructurado con los datos extraídos
    """
)
async def analyze_image(
    file: UploadFile = File(..., description="Imagen del documento"),
    doc_type: Literal["oferta", "mapa", "kardex"] = Form(
        ..., description="Tipo de documento"
    ),
    use_pro: bool = Form(
        False, description="Usar Gemini Pro (más preciso pero más lento)"
    ),
    current_user: Estudiante = Depends(get_current_user)
):
    """Analiza una imagen o PDF de documento académico.
    
    Args:
        file: Archivo de imagen o PDF subido
        doc_type: Tipo de documento (oferta, mapa, kardex)
        use_pro: Usar Gemini Pro para mayor precisión
        current_user: Usuario autenticado
        
    Returns:
        VisionAnalyzeResponse con los datos extraídos
        
    Raises:
        HTTPException 400: Archivo inválido
        HTTPException 503: Error en servicio de IA
    """
    logger.info(
        f"Analyze request: user={current_user.id}, doc_type={doc_type}, "
        f"file={file.filename}, content_type={file.content_type}, size={file.size}"
    )
    
    # Validar content type
    if not file.content_type or file.content_type not in SUPPORTED_TYPES:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Formato no soportado: {file.content_type}. "
                   f"Soportados: imágenes (JPG, PNG, GIF, WEBP) y PDF"
        )
    
    # Leer archivo
    try:
        file_data = await file.read()
    except Exception as e:
        logger.error(f"Error leyendo archivo: {e}")
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Error leyendo el archivo"
        )
    
    # Analizar con Vision Service
    try:
        service = get_vision_service()
        
        # Elegir método según tipo de archivo
        if is_pdf(file.content_type):
            result = await service.analyze_pdf(
                pdf_data=file_data,
                doc_type=doc_type,
                use_pro=use_pro
            )
        else:
            result = await service.analyze_image(
                image_data=file_data,
                doc_type=doc_type,
                use_pro=use_pro
            )
        
        # Verificar si hubo error interno
        if result.get("error"):
            raise HTTPException(
                status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
                detail=result.get("message", "Error procesando archivo")
            )
        
        # Extraer metadata
        metadata = result.pop("_metadata", None)
        
        return VisionAnalyzeResponse(
            success=True,
            doc_type=doc_type,
            data=result,
            metadata=metadata
        )
        
    except ImageValidationError as e:
        logger.warning(f"Imagen inválida: {e}")
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )
    except GeminiAPIError as e:
        logger.error(f"Error Gemini API: {e}")
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail=str(e)
        )
    except Exception as e:
        logger.exception(f"Error inesperado en analyze: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Error interno procesando el archivo"
        )


@router.post(
    "/analyze-test",
    response_model=VisionAnalyzeResponse,
    summary="[DEV] Analizar imagen/PDF sin autenticación",
    description="Endpoint de prueba para desarrollo. No requiere autenticación. Soporta imágenes y PDFs.",
    include_in_schema=True  # Cambiar a False en producción
)
async def analyze_file_test(
    file: UploadFile = File(..., description="Imagen o PDF del documento"),
    doc_type: Literal["oferta", "mapa", "kardex"] = Form(
        ..., description="Tipo de documento"
    ),
    use_pro: bool = Form(
        False, description="Usar Gemini Pro"
    )
):
    """Versión de prueba sin autenticación.
    
    ⚠️ SOLO PARA DESARROLLO - Deshabilitar en producción.
    Soporta imágenes (JPG, PNG, GIF, WEBP) y PDFs.
    """
    logger.info(
        f"[TEST] Analyze request: doc_type={doc_type}, "
        f"file={file.filename}, content_type={file.content_type}, size={file.size}"
    )
    
    # Validar content type
    if not file.content_type or file.content_type not in SUPPORTED_TYPES:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Formato no soportado: {file.content_type}. "
                   f"Soportados: imágenes (JPG, PNG, GIF, WEBP) y PDF"
        )
    
    # Leer archivo
    try:
        file_data = await file.read()
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Error leyendo el archivo"
        )
    
    # Analizar
    try:
        service = get_vision_service()
        
        # Elegir método según tipo de archivo
        if is_pdf(file.content_type):
            result = await service.analyze_pdf(
                pdf_data=file_data,
                doc_type=doc_type,
                use_pro=use_pro
            )
        else:
            result = await service.analyze_image(
                image_data=file_data,
                doc_type=doc_type,
                use_pro=use_pro
            )
        
        if result.get("error"):
            raise HTTPException(
                status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
                detail=result.get("message", "Error procesando archivo")
            )
        
        metadata = result.pop("_metadata", None)
        
        return VisionAnalyzeResponse(
            success=True,
            doc_type=doc_type,
            data=result,
            metadata=metadata
        )
        
    except ImageValidationError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )
    except GeminiAPIError as e:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail=str(e)
        )
    except Exception as e:
        logger.exception(f"Error en analyze-test: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Error interno procesando la imagen"
        )
