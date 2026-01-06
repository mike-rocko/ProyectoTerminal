"""
Servicio para procesar imágenes y PDFs con Gemini Vision API.

Este servicio maneja:
- Validación y preprocesamiento de imágenes
- Conversión de PDFs a imágenes
- Llamadas a Gemini Vision API
- Parsing y validación de respuestas JSON
"""
import base64
import json
import logging
from io import BytesIO
from pathlib import Path
from typing import List, Literal, Optional, Union

import fitz  # PyMuPDF
from PIL import Image
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_core.messages import HumanMessage

from app.core.config import settings
from app.tools.prompts.vision_prompts import get_prompt

logger = logging.getLogger(__name__)

# Tipos de documento soportados
DocType = Literal["oferta", "mapa", "kardex"]

# Configuración de imagen
MAX_IMAGE_SIZE_MB = 10
MAX_PDF_SIZE_MB = 20
MAX_PDF_PAGES = 10
MIN_IMAGE_WIDTH = 200
MIN_IMAGE_HEIGHT = 200
SUPPORTED_IMAGE_FORMATS = {"JPEG", "PNG", "GIF", "WEBP"}
PDF_DPI = 150  # Resolución para convertir PDF a imagen


class VisionServiceError(Exception):
    """Excepción base para errores del servicio de visión."""
    pass


class ImageValidationError(VisionServiceError):
    """Error en la validación de imagen."""
    pass


class GeminiAPIError(VisionServiceError):
    """Error en la llamada a Gemini API."""
    pass


class VisionService:
    """Servicio para analizar imágenes académicas con Gemini Vision."""
    
    def __init__(self):
        """Inicializa el servicio con el modelo Gemini Vision."""
        self.llm = ChatGoogleGenerativeAI(
            model="gemini-2.5-flash",  # Modelo más nuevo y rápido
            google_api_key=settings.google_api_key,
            temperature=0,  # Respuestas determinísticas
            max_output_tokens=8192,  # Aumentado para documentos grandes
        )
        # Pro para imágenes más complejas
        self.llm_pro = ChatGoogleGenerativeAI(
            model="gemini-2.5-pro",
            google_api_key=settings.google_api_key,
            temperature=0,
            max_output_tokens=16384,  # Más tokens para Pro
        )
    
    def pdf_to_images(self, pdf_data: bytes) -> List[bytes]:
        """Convierte un PDF a una lista de imágenes.
        
        Args:
            pdf_data: Bytes del archivo PDF
            
        Returns:
            Lista de bytes de imágenes (PNG)
            
        Raises:
            ImageValidationError: Si el PDF no es válido o muy grande
        """
        size_mb = len(pdf_data) / (1024 * 1024)
        if size_mb > MAX_PDF_SIZE_MB:
            raise ImageValidationError(
                f"PDF muy grande: {size_mb:.1f}MB (máximo: {MAX_PDF_SIZE_MB}MB)"
            )
        
        try:
            doc = fitz.open(stream=pdf_data, filetype="pdf")
        except Exception as e:
            raise ImageValidationError(f"No se pudo abrir el PDF: {e}")
        
        if doc.page_count > MAX_PDF_PAGES:
            raise ImageValidationError(
                f"PDF tiene muchas páginas: {doc.page_count} (máximo: {MAX_PDF_PAGES})"
            )
        
        images = []
        for page_num in range(doc.page_count):
            page = doc[page_num]
            # Convertir página a imagen con resolución especificada
            mat = fitz.Matrix(PDF_DPI / 72, PDF_DPI / 72)
            pix = page.get_pixmap(matrix=mat)
            
            # Convertir a PNG bytes
            img_bytes = pix.tobytes("png")
            images.append(img_bytes)
            
            logger.debug(f"Convertida página {page_num + 1}/{doc.page_count}")
        
        doc.close()
        logger.info(f"PDF convertido: {len(images)} páginas")
        return images
    
    def validate_image(self, image_data: bytes) -> Image.Image:
        """Valida que la imagen cumpla los requisitos mínimos.
        
        Args:
            image_data: Bytes de la imagen
            
        Returns:
            Objeto PIL Image validado
            
        Raises:
            ImageValidationError: Si la imagen no es válida
        """
        # Verificar tamaño
        size_mb = len(image_data) / (1024 * 1024)
        if size_mb > MAX_IMAGE_SIZE_MB:
            raise ImageValidationError(
                f"Imagen muy grande: {size_mb:.1f}MB (máximo: {MAX_IMAGE_SIZE_MB}MB)"
            )
        
        # Intentar abrir imagen
        try:
            image = Image.open(BytesIO(image_data))
        except Exception as e:
            raise ImageValidationError(f"No se pudo abrir la imagen: {e}")
        
        # Verificar formato
        if image.format not in SUPPORTED_IMAGE_FORMATS:
            raise ImageValidationError(
                f"Formato no soportado: {image.format}. "
                f"Soportados: {SUPPORTED_IMAGE_FORMATS}"
            )
        
        # Verificar dimensiones mínimas
        width, height = image.size
        if width < MIN_IMAGE_WIDTH or height < MIN_IMAGE_HEIGHT:
            raise ImageValidationError(
                f"Imagen muy pequeña: {width}x{height}. "
                f"Mínimo: {MIN_IMAGE_WIDTH}x{MIN_IMAGE_HEIGHT}"
            )
        
        logger.info(f"Imagen validada: {image.format} {width}x{height} ({size_mb:.1f}MB)")
        return image
    
    def _image_to_base64(self, image_data: bytes) -> str:
        """Convierte bytes de imagen a base64.
        
        Args:
            image_data: Bytes de la imagen
            
        Returns:
            String base64 de la imagen
        """
        return base64.standard_b64encode(image_data).decode("utf-8")
    
    def _get_mime_type(self, image: Image.Image) -> str:
        """Obtiene el MIME type de la imagen.
        
        Args:
            image: Objeto PIL Image
            
        Returns:
            String con MIME type (ej: "image/jpeg")
        """
        format_to_mime = {
            "JPEG": "image/jpeg",
            "PNG": "image/png",
            "GIF": "image/gif",
            "WEBP": "image/webp",
        }
        return format_to_mime.get(image.format, "image/jpeg")
    
    def _parse_json_response(self, response_text: str) -> dict:
        """Parsea la respuesta JSON del LLM, limpiando markdown si es necesario.
        
        Args:
            response_text: Texto de respuesta del LLM
            
        Returns:
            Diccionario con los datos extraídos
            
        Raises:
            GeminiAPIError: Si no se puede parsear el JSON
        """
        import re
        
        text = response_text.strip()
        
        # Limpiar markdown code blocks si existen
        if text.startswith("```json"):
            text = text[7:]
        elif text.startswith("```"):
            text = text[3:]
        
        if text.endswith("```"):
            text = text[:-3]
        
        text = text.strip()
        
        # Intento 1: parsear directamente
        try:
            return json.loads(text)
        except json.JSONDecodeError:
            pass
        
        # Intento 2: limpiar trailing commas (error común de LLMs)
        try:
            # Remover comas antes de } o ]
            cleaned = re.sub(r',\s*([}\]])', r'\1', text)
            return json.loads(cleaned)
        except json.JSONDecodeError:
            pass
        
        # Intento 3: buscar el JSON dentro del texto
        try:
            # Encontrar el primer { y el último }
            start = text.find('{')
            end = text.rfind('}') + 1
            if start != -1 and end > start:
                json_str = text[start:end]
                cleaned = re.sub(r',\s*([}\]])', r'\1', json_str)
                return json.loads(cleaned)
        except json.JSONDecodeError as e:
            logger.error(f"Error parseando JSON: {e}\nTexto: {text[:500]}...")
            raise GeminiAPIError(f"Respuesta no es JSON válido: {e}")
    
    async def analyze_image(
        self,
        image_data: bytes,
        doc_type: DocType,
        use_pro: bool = False
    ) -> dict:
        """Analiza una imagen y extrae datos estructurados.
        
        Args:
            image_data: Bytes de la imagen a analizar
            doc_type: Tipo de documento ("oferta", "mapa", "kardex")
            use_pro: Si True, usa Gemini Pro (más lento pero más preciso)
            
        Returns:
            Diccionario con los datos extraídos según el tipo de documento
            
        Raises:
            ImageValidationError: Si la imagen no es válida
            GeminiAPIError: Si hay error en la API
        """
        # Validar imagen
        image = self.validate_image(image_data)
        
        # Obtener prompt
        prompt = get_prompt(doc_type)
        
        # Convertir a base64
        image_base64 = self._image_to_base64(image_data)
        mime_type = self._get_mime_type(image)
        
        # Crear mensaje con imagen
        message = HumanMessage(
            content=[
                {
                    "type": "image_url",
                    "image_url": {
                        "url": f"data:{mime_type};base64,{image_base64}"
                    }
                },
                {
                    "type": "text",
                    "text": prompt
                }
            ]
        )
        
        # Seleccionar modelo
        llm = self.llm_pro if use_pro else self.llm
        model_name = "gemini-1.5-pro" if use_pro else "gemini-1.5-flash"
        
        logger.info(f"Analizando imagen tipo '{doc_type}' con {model_name}...")
        
        try:
            # Llamar a Gemini (async)
            response = await llm.ainvoke([message])
            response_text = response.content
            
            logger.debug(f"Respuesta raw: {response_text[:200]}...")
            
            # Parsear JSON
            result = self._parse_json_response(response_text)
            
            # Agregar metadata
            result["_metadata"] = {
                "doc_type": doc_type,
                "model": model_name,
                "image_size": f"{image.size[0]}x{image.size[1]}",
                "image_format": image.format
            }
            
            logger.info(f"Análisis completado exitosamente para tipo '{doc_type}'")
            return result
            
        except Exception as e:
            if "quota" in str(e).lower() or "rate" in str(e).lower():
                raise GeminiAPIError(
                    "Límite de API alcanzado. Espera un momento e intenta de nuevo."
                )
            logger.error(f"Error en Gemini API: {e}")
            raise GeminiAPIError(f"Error procesando imagen: {e}")
    
    async def analyze_from_path(
        self,
        image_path: Union[str, Path],
        doc_type: DocType,
        use_pro: bool = False
    ) -> dict:
        """Analiza una imagen desde una ruta de archivo.
        
        Args:
            image_path: Ruta al archivo de imagen
            doc_type: Tipo de documento
            use_pro: Si True, usa Gemini Pro
            
        Returns:
            Diccionario con los datos extraídos
        """
        path = Path(image_path)
        if not path.exists():
            raise ImageValidationError(f"Archivo no encontrado: {path}")
        
        image_data = path.read_bytes()
        return await self.analyze_image(image_data, doc_type, use_pro)
    
    async def analyze_pdf(
        self,
        pdf_data: bytes,
        doc_type: DocType,
        use_pro: bool = False
    ) -> dict:
        """Analiza un PDF de múltiples páginas y combina los resultados.
        
        Convierte cada página a imagen, las analiza, y combina los resultados
        en un único diccionario coherente.
        
        Args:
            pdf_data: Bytes del archivo PDF
            doc_type: Tipo de documento ("oferta", "mapa", "kardex")
            use_pro: Si True, usa Gemini Pro
            
        Returns:
            Diccionario con datos combinados de todas las páginas
        """
        import asyncio
        
        # Convertir PDF a imágenes
        images = self.pdf_to_images(pdf_data)
        logger.info(f"Analizando PDF con {len(images)} páginas como tipo '{doc_type}'")
        
        all_results = []
        
        for i, img_data in enumerate(images):
            logger.info(f"Procesando página {i + 1}/{len(images)}...")
            try:
                result = await self.analyze_image(img_data, doc_type, use_pro)
                result["_page"] = i + 1
                all_results.append(result)
                
                # Delay entre páginas para evitar rate limiting (30 segundos)
                if i < len(images) - 1:
                    logger.debug("Esperando 30s para evitar rate limit...")
                    await asyncio.sleep(30)
                    
            except Exception as e:
                logger.warning(f"Error en página {i + 1}: {e}")
                all_results.append({"_page": i + 1, "_error": str(e)})
        
        # Combinar resultados según el tipo de documento
        combined = self._combine_results(all_results, doc_type)
        combined["_metadata"] = {
            "doc_type": doc_type,
            "source": "pdf",
            "total_pages": len(images),
            "pages_processed": len([r for r in all_results if "_error" not in r])
        }
        
        return combined
    
    def _combine_results(self, results: List[dict], doc_type: DocType) -> dict:
        """Combina resultados de múltiples páginas en uno solo.
        
        Args:
            results: Lista de resultados por página
            doc_type: Tipo de documento
            
        Returns:
            Diccionario combinado
        """
        # Filtrar páginas con errores
        valid_results = [r for r in results if "_error" not in r]
        
        if not valid_results:
            return {"error": True, "message": "No se pudo procesar ninguna página"}
        
        if doc_type == "kardex":
            # Para kárdex: combinar estudiante (tomar primero) y todos los periodos
            combined = {
                "estudiante": None,
                "periodos": [],
                "resumen": None,
                "notas": None
            }
            
            for result in valid_results:
                # Estudiante: tomar el primero que tenga datos
                if combined["estudiante"] is None and result.get("estudiante"):
                    combined["estudiante"] = result["estudiante"]
                
                # Periodos: agregar todos
                if result.get("periodos"):
                    combined["periodos"].extend(result["periodos"])
                
                # Resumen: tomar el último (suele estar en última página)
                if result.get("resumen"):
                    combined["resumen"] = result["resumen"]
                    
            return combined
            
        elif doc_type == "oferta":
            # Para oferta: combinar todas las materias
            combined = {
                "semestre": None,
                "universidad": None,
                "materias": [],
                "notas": None
            }
            
            for result in valid_results:
                if combined["semestre"] is None and result.get("semestre"):
                    combined["semestre"] = result["semestre"]
                if combined["universidad"] is None and result.get("universidad"):
                    combined["universidad"] = result["universidad"]
                if result.get("materias"):
                    combined["materias"].extend(result["materias"])
                    
            return combined
            
        elif doc_type == "mapa":
            # Para mapa: combinar semestres
            combined = {
                "carrera": None,
                "plan": None,
                "total_creditos": None,
                "duracion_semestres": None,
                "semestres": [],
                "areas_formacion": [],
                "notas": None
            }
            
            for result in valid_results:
                if combined["carrera"] is None and result.get("carrera"):
                    combined["carrera"] = result["carrera"]
                if combined["plan"] is None and result.get("plan"):
                    combined["plan"] = result["plan"]
                if result.get("total_creditos"):
                    combined["total_creditos"] = result["total_creditos"]
                if result.get("semestres"):
                    combined["semestres"].extend(result["semestres"])
                if result.get("areas_formacion"):
                    combined["areas_formacion"].extend(result["areas_formacion"])
                    
            return combined
        
        # Default: retornar primer resultado válido
        return valid_results[0]


# Singleton del servicio
_vision_service: Optional[VisionService] = None


def get_vision_service() -> VisionService:
    """Obtiene la instancia singleton del servicio de visión.
    
    Returns:
        Instancia de VisionService
    """
    global _vision_service
    if _vision_service is None:
        _vision_service = VisionService()
    return _vision_service
