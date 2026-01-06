"""
Servicio RAG (Retrieval Augmented Generation).

Maneja la ingestión de documentos y búsqueda semántica usando:
- Google Generative AI Embeddings
- PostgreSQL pgvector para búsqueda vectorial
- Gemini para generación de respuestas
"""
import logging
import time
from typing import Any, Dict, List, Optional, Tuple
from uuid import UUID

from langchain_google_genai import GoogleGenerativeAIEmbeddings, ChatGoogleGenerativeAI
from langchain.text_splitter import RecursiveCharacterTextSplitter
from sqlalchemy import delete, func, select, text
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.config import settings
from app.models.universidad_info import UniversidadInfo, TIPOS_DOCUMENTO
from app.schemas.rag import (
    ChunkCreated,
    DocumentoIngestRequest,
    DocumentoIngestResponse,
    RAGAnswerRequest,
    RAGAnswerResponse,
    RAGQueryRequest,
    RAGQueryResponse,
    RAGResult,
    SourceReference,
)

logger = logging.getLogger(__name__)


class RAGService:
    """Servicio para operaciones RAG.
    
    Proporciona:
    - Ingestión de documentos con chunking y embedding
    - Búsqueda semántica con pgvector
    - Generación de respuestas con Gemini
    """
    
    def __init__(self):
        """Inicializa embeddings y LLM."""
        self.embeddings = GoogleGenerativeAIEmbeddings(
            model="models/embedding-001",
            google_api_key=settings.google_api_key
        )
        
        self.llm = ChatGoogleGenerativeAI(
            model="gemini-2.5-flash",
            google_api_key=settings.google_api_key,
            temperature=0.3,  # Más determinístico para respuestas factuales
        )
        
        self.text_splitter = RecursiveCharacterTextSplitter(
            chunk_size=500,
            chunk_overlap=50,
            length_function=len,
            separators=["\n\n", "\n", ". ", " ", ""]
        )
    
    def _split_text(
        self,
        text: str,
        chunk_size: int = 500,
        chunk_overlap: int = 50
    ) -> List[str]:
        """Divide texto en chunks con overlap.
        
        Args:
            text: Texto a dividir
            chunk_size: Tamaño máximo por chunk
            chunk_overlap: Overlap entre chunks
            
        Returns:
            Lista de chunks
        """
        splitter = RecursiveCharacterTextSplitter(
            chunk_size=chunk_size,
            chunk_overlap=chunk_overlap,
            length_function=len,
            separators=["\n\n", "\n", ". ", " ", ""]
        )
        return splitter.split_text(text)
    
    async def embed_text(self, text: str) -> List[float]:
        """Genera embedding para un texto.
        
        Args:
            text: Texto a embeber
            
        Returns:
            Vector de 768 dimensiones
        """
        try:
            # LangChain embeddings usa sync, pero wrapeamos
            embedding = self.embeddings.embed_query(text)
            return embedding
        except Exception as e:
            logger.error(f"Error generando embedding: {e}")
            raise
    
    async def embed_texts(self, texts: List[str]) -> List[List[float]]:
        """Genera embeddings para múltiples textos.
        
        Args:
            texts: Lista de textos
            
        Returns:
            Lista de vectores
        """
        try:
            embeddings = self.embeddings.embed_documents(texts)
            return embeddings
        except Exception as e:
            logger.error(f"Error generando embeddings: {e}")
            raise
    
    async def ingest_document(
        self,
        db: AsyncSession,
        request: DocumentoIngestRequest
    ) -> DocumentoIngestResponse:
        """Ingesta un documento dividiéndolo en chunks con embeddings.
        
        Args:
            db: Sesión de base de datos async
            request: Datos del documento
            
        Returns:
            Response con info de chunks creados
        """
        start_time = time.time()
        
        try:
            # Validar tipo
            if request.tipo not in TIPOS_DOCUMENTO:
                raise ValueError(f"Tipo inválido. Debe ser uno de: {TIPOS_DOCUMENTO}")
            
            # Dividir en chunks
            chunks = self._split_text(
                request.contenido,
                chunk_size=request.chunk_size,
                chunk_overlap=request.chunk_overlap
            )
            
            logger.info(f"Documento dividido en {len(chunks)} chunks")
            
            # Generar embeddings para todos los chunks
            embeddings = await self.embed_texts(chunks)
            
            # Crear registros en DB
            chunks_created: List[ChunkCreated] = []
            
            for i, (chunk_text, embedding) in enumerate(zip(chunks, embeddings)):
                # Crear metadata con número de chunk
                chunk_metadata = request.metadata.copy() if request.metadata else {}
                chunk_metadata["chunk_index"] = i
                chunk_metadata["total_chunks"] = len(chunks)
                
                info = UniversidadInfo(
                    universidad_id=request.universidad_id,
                    tipo=request.tipo,
                    titulo=request.titulo,
                    contenido=chunk_text,
                    embedding=embedding,
                    extra_data=chunk_metadata,  # Usar extra_data en lugar de metadata
                    source_url=request.source_url
                )
                
                db.add(info)
                await db.flush()  # Para obtener el ID
                
                chunks_created.append(ChunkCreated(
                    id=info.id,
                    contenido_preview=chunk_text[:100] + "..." if len(chunk_text) > 100 else chunk_text,
                    caracteres=len(chunk_text)
                ))
            
            await db.commit()
            
            elapsed_ms = (time.time() - start_time) * 1000
            
            return DocumentoIngestResponse(
                success=True,
                mensaje=f"Documento '{request.titulo}' ingestado exitosamente",
                chunks_creados=len(chunks_created),
                chunks=chunks_created,
                tiempo_procesamiento_ms=elapsed_ms
            )
            
        except Exception as e:
            await db.rollback()
            logger.exception(f"Error en ingestión: {e}")
            raise
    
    async def search_similar(
        self,
        db: AsyncSession,
        request: RAGQueryRequest
    ) -> RAGQueryResponse:
        """Busca chunks similares usando búsqueda vectorial.
        
        Args:
            db: Sesión de base de datos
            request: Query con universidad_id y pregunta
            
        Returns:
            Resultados ordenados por similitud
        """
        start_time = time.time()
        
        try:
            # Generar embedding de la query
            query_embedding = await self.embed_text(request.query)
            
            # Construir query SQL con pgvector
            # Usamos 1 - distancia_coseno como score de similitud
            base_query = """
                SELECT 
                    id,
                    tipo,
                    titulo,
                    contenido,
                    metadata,
                    source_url,
                    1 - (embedding <=> :query_embedding::vector) as score
                FROM universidad_info
                WHERE universidad_id = :universidad_id
            """
            
            # Filtrar por tipos si se especifican
            if request.tipos:
                tipos_str = ", ".join([f"'{t}'" for t in request.tipos])
                base_query += f" AND tipo IN ({tipos_str})"
            
            # Filtrar por umbral y ordenar
            base_query += """
                AND 1 - (embedding <=> :query_embedding::vector) >= :threshold
                ORDER BY embedding <=> :query_embedding::vector
                LIMIT :limit
            """
            
            result = await db.execute(
                text(base_query),
                {
                    "query_embedding": str(query_embedding),
                    "universidad_id": str(request.universidad_id),
                    "threshold": request.score_threshold,
                    "limit": request.top_k
                }
            )
            
            rows = result.fetchall()
            
            # Construir resultados
            resultados: List[RAGResult] = []
            contenidos: List[str] = []
            
            for row in rows:
                resultado = RAGResult(
                    id=row.id,
                    tipo=row.tipo,
                    titulo=row.titulo,
                    contenido=row.contenido,
                    score=float(row.score),
                    metadata=row.metadata if request.include_metadata else None,
                    source_url=row.source_url
                )
                resultados.append(resultado)
                contenidos.append(f"[{row.tipo}: {row.titulo}]\n{row.contenido}")
            
            # Concatenar contexto para LLM
            contexto_combinado = "\n\n---\n\n".join(contenidos) if contenidos else ""
            
            elapsed_ms = (time.time() - start_time) * 1000
            
            return RAGQueryResponse(
                success=True,
                query=request.query,
                resultados=resultados,
                total_encontrados=len(resultados),
                contexto_combinado=contexto_combinado,
                tiempo_busqueda_ms=elapsed_ms
            )
            
        except Exception as e:
            logger.exception(f"Error en búsqueda: {e}")
            raise
    
    async def generate_answer(
        self,
        db: AsyncSession,
        request: RAGAnswerRequest
    ) -> RAGAnswerResponse:
        """Genera respuesta usando RAG: busca contexto + genera con LLM.
        
        Args:
            db: Sesión de base de datos
            request: Query del usuario
            
        Returns:
            Respuesta generada con fuentes
        """
        start_time = time.time()
        
        try:
            # 1. Buscar contexto relevante
            search_request = RAGQueryRequest(
                universidad_id=request.universidad_id,
                query=request.query,
                tipos=request.tipos,
                top_k=request.top_k,
                score_threshold=0.4,  # Umbral más bajo para obtener más contexto
                include_metadata=True
            )
            
            search_response = await self.search_similar(db, search_request)
            
            # 2. Verificar si hay suficiente contexto
            advertencia = None
            if not search_response.resultados:
                advertencia = "No se encontró información relacionada con tu pregunta."
                return RAGAnswerResponse(
                    success=True,
                    query=request.query,
                    respuesta="Lo siento, no tengo información sobre ese tema en mi base de conocimiento. "
                              "Te sugiero contactar directamente a la universidad para esta consulta.",
                    fuentes=[],
                    confianza=0.0,
                    advertencia=advertencia,
                    tiempo_total_ms=(time.time() - start_time) * 1000
                )
            
            # Calcular confianza promedio
            avg_score = sum(r.score for r in search_response.resultados) / len(search_response.resultados)
            
            if avg_score < 0.5:
                advertencia = "La información encontrada podría no ser completamente relevante."
            
            # 3. Construir prompt para Gemini
            prompt = self._build_rag_prompt(
                query=request.query,
                contexto=search_response.contexto_combinado
            )
            
            # 4. Generar respuesta con LLM
            response = await self.llm.ainvoke(prompt)
            respuesta_texto = response.content
            
            # 5. Construir fuentes
            fuentes = []
            if request.include_sources:
                for r in search_response.resultados:
                    fuentes.append(SourceReference(
                        titulo=r.titulo,
                        tipo=r.tipo,
                        relevancia=r.score,
                        source_url=r.source_url
                    ))
            
            elapsed_ms = (time.time() - start_time) * 1000
            
            return RAGAnswerResponse(
                success=True,
                query=request.query,
                respuesta=respuesta_texto,
                fuentes=fuentes,
                confianza=avg_score,
                advertencia=advertencia,
                tiempo_total_ms=elapsed_ms
            )
            
        except Exception as e:
            logger.exception(f"Error generando respuesta: {e}")
            raise
    
    def _build_rag_prompt(self, query: str, contexto: str) -> str:
        """Construye el prompt para el LLM.
        
        Args:
            query: Pregunta del usuario
            contexto: Contexto recuperado del RAG
            
        Returns:
            Prompt formateado
        """
        return f"""Eres un asistente virtual de la universidad. Tu rol es responder preguntas 
de estudiantes de manera amable, clara y precisa usando ÚNICAMENTE la información proporcionada.

CONTEXTO DISPONIBLE:
{contexto}

REGLAS:
1. Responde SOLO basándote en el contexto proporcionado
2. Si la información no está en el contexto, di que no tienes esa información
3. Cita las fuentes cuando sea relevante (ej: "Según el Reglamento de Inscripciones...")
4. Sé conciso pero completo
5. Si hay fechas o números específicos, menciónalos exactamente
6. Usa un tono amable y profesional

PREGUNTA DEL ESTUDIANTE:
{query}

RESPUESTA:"""
    
    async def delete_documents(
        self,
        db: AsyncSession,
        universidad_id: UUID,
        tipo: Optional[str] = None,
        titulo: Optional[str] = None
    ) -> int:
        """Elimina documentos de una universidad.
        
        Args:
            db: Sesión de base de datos
            universidad_id: ID de la universidad
            tipo: Filtrar por tipo (opcional)
            titulo: Filtrar por título (opcional)
            
        Returns:
            Número de chunks eliminados
        """
        try:
            query = delete(UniversidadInfo).where(
                UniversidadInfo.universidad_id == universidad_id
            )
            
            if tipo:
                query = query.where(UniversidadInfo.tipo == tipo)
            
            if titulo:
                query = query.where(UniversidadInfo.titulo == titulo)
            
            result = await db.execute(query)
            await db.commit()
            
            return result.rowcount
            
        except Exception as e:
            await db.rollback()
            logger.exception(f"Error eliminando documentos: {e}")
            raise
    
    async def get_stats(
        self,
        db: AsyncSession,
        universidad_id: UUID
    ) -> Dict[str, Any]:
        """Obtiene estadísticas de documentos de una universidad.
        
        Args:
            db: Sesión de base de datos
            universidad_id: ID de la universidad
            
        Returns:
            Diccionario con estadísticas
        """
        try:
            # Contar por tipo
            query = select(
                UniversidadInfo.tipo,
                func.count(UniversidadInfo.id).label("count")
            ).where(
                UniversidadInfo.universidad_id == universidad_id
            ).group_by(
                UniversidadInfo.tipo
            )
            
            result = await db.execute(query)
            por_tipo = {row.tipo: row.count for row in result}
            
            # Total
            total = sum(por_tipo.values())
            
            return {
                "total_chunks": total,
                "por_tipo": por_tipo,
                "tipos_disponibles": list(por_tipo.keys())
            }
            
        except Exception as e:
            logger.exception(f"Error obteniendo stats: {e}")
            raise


# Singleton
_rag_service: Optional[RAGService] = None


def get_rag_service() -> RAGService:
    """Obtiene instancia singleton del RAG Service."""
    global _rag_service
    if _rag_service is None:
        _rag_service = RAGService()
    return _rag_service
