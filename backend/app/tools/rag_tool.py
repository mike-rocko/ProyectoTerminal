"""
LangChain Tool para consultas RAG sobre información de la universidad.

Este tool es compatible con LangGraph y permite al agente responder
preguntas sobre reglamentos, calendarios, trámites, etc.
"""
import asyncio
import logging
from typing import Any, Dict, List, Optional, Type
from uuid import UUID

from langchain.tools import BaseTool
from pydantic import BaseModel, Field

from app.models.universidad_info import TIPOS_DOCUMENTO

logger = logging.getLogger(__name__)


class RAGToolInput(BaseModel):
    """Esquema de entrada para el RAG Tool."""
    
    query: str = Field(
        ...,
        description="""La pregunta del estudiante sobre la universidad.
        Ejemplos:
        - "¿Cuál es la fecha límite de inscripciones?"
        - "¿Cuántas materias puedo inscribir?"
        - "¿Dónde está la oficina de servicios escolares?"
        - "¿Cuáles son los requisitos para beca?"
        """
    )
    
    tipos: Optional[List[str]] = Field(
        default=None,
        description=f"""Filtrar por tipos de documento (opcional).
        Tipos disponibles: {', '.join(TIPOS_DOCUMENTO[:8])}
        Si no se especifica, busca en todos los tipos.
        """
    )
    
    universidad_id: Optional[str] = Field(
        default=None,
        description="""ID de la universidad (UUID). 
        Si no se proporciona, se usa el contexto del estudiante actual.
        """
    )


class RAGTool(BaseTool):
    """Herramienta para consultar información de la universidad.
    
    Usa búsqueda semántica (RAG) para encontrar información relevante
    en reglamentos, calendarios, FAQs y otros documentos de la universidad.
    
    Examples:
        >>> tool = RAGTool()
        >>> result = tool._run(
        ...     query="¿Cuál es la fecha límite de inscripciones?",
        ...     tipos=["calendario", "reglamento"]
        ... )
    """
    
    name: str = "universidad_info"
    description: str = """
    Consulta información oficial de la universidad.
    
    Usa esta herramienta cuando el estudiante pregunte sobre:
    - Fechas importantes (inscripciones, exámenes, vacaciones)
    - Reglamentos y normativas
    - Trámites y procedimientos
    - Información de contacto
    - Servicios universitarios
    - Requisitos de becas
    - Cualquier otra información institucional
    
    La herramienta busca en documentos oficiales y responde con información verificada.
    Siempre indica la fuente de la información.
    
    NO uses esta herramienta para:
    - Información sobre materias específicas (usa vision_tool)
    - Generar horarios (usa schedule_builder)
    - Análisis de documentos del estudiante (usa vision_tool)
    """
    args_schema: Type[BaseModel] = RAGToolInput
    
    # Contexto que puede ser inyectado por el agente
    _universidad_id: Optional[str] = None
    _db_session_factory: Optional[Any] = None
    
    def set_context(
        self,
        universidad_id: str,
        db_session_factory: Any
    ) -> None:
        """Inyecta contexto necesario para el tool.
        
        Args:
            universidad_id: ID de la universidad del estudiante
            db_session_factory: Factory para crear sesiones de DB
        """
        self._universidad_id = universidad_id
        self._db_session_factory = db_session_factory
    
    def _run(
        self,
        query: str,
        tipos: Optional[List[str]] = None,
        universidad_id: Optional[str] = None
    ) -> Dict[str, Any]:
        """Versión sync del tool (usa asyncio.run internamente)."""
        try:
            loop = asyncio.get_event_loop()
            if loop.is_running():
                # Si ya hay un event loop, creamos uno nuevo en un thread
                import concurrent.futures
                with concurrent.futures.ThreadPoolExecutor() as executor:
                    future = executor.submit(
                        asyncio.run,
                        self._arun(query, tipos, universidad_id)
                    )
                    return future.result()
            else:
                return asyncio.run(self._arun(query, tipos, universidad_id))
        except Exception as e:
            logger.exception(f"RAGTool sync error: {e}")
            return {
                "success": False,
                "error": str(e),
                "respuesta": f"Error consultando información: {e}"
            }
    
    async def _arun(
        self,
        query: str,
        tipos: Optional[List[str]] = None,
        universidad_id: Optional[str] = None
    ) -> Dict[str, Any]:
        """Consulta información de la universidad.
        
        Args:
            query: Pregunta del estudiante
            tipos: Tipos de documento a buscar
            universidad_id: ID de universidad (override)
            
        Returns:
            Diccionario con respuesta y fuentes
        """
        logger.info(f"RAGTool: Buscando '{query[:50]}...'")
        
        try:
            # Importar aquí para evitar circular imports
            from app.services.rag_service import get_rag_service
            from app.schemas.rag import RAGAnswerRequest
            from app.db.session import AsyncSessionLocal
            
            # Determinar universidad_id
            uni_id = universidad_id or self._universidad_id
            if not uni_id:
                return {
                    "success": False,
                    "error": "No se proporcionó universidad_id",
                    "respuesta": "No puedo determinar tu universidad. Por favor proporciona el ID."
                }
            
            # Parsear UUID
            try:
                uni_uuid = UUID(uni_id) if isinstance(uni_id, str) else uni_id
            except ValueError:
                return {
                    "success": False,
                    "error": f"universidad_id inválido: {uni_id}",
                    "respuesta": "ID de universidad inválido."
                }
            
            # Usar session factory inyectada o crear nueva
            if self._db_session_factory:
                async with self._db_session_factory() as db:
                    return await self._execute_query(db, query, tipos, uni_uuid)
            else:
                async with AsyncSessionLocal() as db:
                    return await self._execute_query(db, query, tipos, uni_uuid)
                    
        except Exception as e:
            logger.exception(f"RAGTool error: {e}")
            return {
                "success": False,
                "error": str(e),
                "respuesta": f"Error consultando información: {e}"
            }
    
    async def _execute_query(
        self,
        db: Any,
        query: str,
        tipos: Optional[List[str]],
        universidad_id: UUID
    ) -> Dict[str, Any]:
        """Ejecuta la consulta RAG.
        
        Args:
            db: Sesión de base de datos
            query: Pregunta
            tipos: Filtro de tipos
            universidad_id: ID de universidad
            
        Returns:
            Resultado de la consulta
        """
        from app.services.rag_service import get_rag_service
        from app.schemas.rag import RAGAnswerRequest
        
        service = get_rag_service()
        
        request = RAGAnswerRequest(
            universidad_id=universidad_id,
            query=query,
            tipos=tipos,
            top_k=5,
            include_sources=True
        )
        
        response = await service.generate_answer(db, request)
        
        # Convertir a diccionario para el agente
        result = {
            "success": response.success,
            "respuesta": response.respuesta,
            "confianza": response.confianza,
            "num_fuentes": len(response.fuentes),
            "fuentes": [
                {
                    "titulo": f.titulo,
                    "tipo": f.tipo,
                    "relevancia": round(f.relevancia, 2),
                    "url": f.source_url
                }
                for f in response.fuentes
            ]
        }
        
        if response.advertencia:
            result["advertencia"] = response.advertencia
        
        logger.info(f"RAGTool: Respuesta generada con {len(response.fuentes)} fuentes")
        
        return result


# Instancia del tool para importar directamente
rag_tool = RAGTool()
