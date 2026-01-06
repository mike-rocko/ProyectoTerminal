"""
Schemas para RAG (Retrieval Augmented Generation).

Modelos para ingestión de documentos y consultas semánticas.
"""
from datetime import datetime
from typing import Any, Dict, List, Literal, Optional
from uuid import UUID

from pydantic import BaseModel, Field

from app.models.universidad_info import TIPOS_DOCUMENTO


# ============================================
# Schemas para Ingestión de Documentos
# ============================================

class DocumentoIngestRequest(BaseModel):
    """Request para ingestar un nuevo documento."""
    
    universidad_id: UUID = Field(
        ...,
        description="ID de la universidad (multi-tenant)"
    )
    
    tipo: str = Field(
        ...,
        description=f"Tipo de documento: {', '.join(TIPOS_DOCUMENTO)}"
    )
    
    titulo: str = Field(
        ...,
        min_length=3,
        max_length=255,
        description="Título del documento"
    )
    
    contenido: str = Field(
        ...,
        min_length=10,
        description="Contenido del documento (se dividirá en chunks automáticamente)"
    )
    
    metadata: Optional[Dict[str, Any]] = Field(
        default=None,
        description="Metadatos adicionales (fecha, autor, versión, etc.)"
    )
    
    source_url: Optional[str] = Field(
        default=None,
        description="URL o path del documento original"
    )
    
    chunk_size: int = Field(
        default=500,
        ge=100,
        le=2000,
        description="Tamaño máximo de cada chunk en caracteres"
    )
    
    chunk_overlap: int = Field(
        default=50,
        ge=0,
        le=200,
        description="Overlap entre chunks para contexto"
    )
    
    model_config = {
        "json_schema_extra": {
            "example": {
                "universidad_id": "123e4567-e89b-12d3-a456-426614174000",
                "tipo": "reglamento",
                "titulo": "Reglamento de Inscripciones 2024",
                "contenido": "Artículo 1. Los estudiantes deberán inscribirse...",
                "metadata": {"version": "2024.1", "fecha": "2024-01-15"},
                "source_url": "https://unicaribe.edu/reglamento.pdf"
            }
        }
    }


class ChunkCreated(BaseModel):
    """Info de un chunk creado."""
    id: UUID
    contenido_preview: str = Field(..., description="Primeros 100 chars")
    caracteres: int


class DocumentoIngestResponse(BaseModel):
    """Response después de ingestar documento."""
    success: bool
    mensaje: str
    chunks_creados: int
    chunks: List[ChunkCreated]
    tiempo_procesamiento_ms: float


class DocumentoDeleteRequest(BaseModel):
    """Request para eliminar documentos."""
    universidad_id: UUID
    tipo: Optional[str] = None  # Si se especifica, solo elimina de ese tipo
    titulo: Optional[str] = None  # Si se especifica, solo ese documento


class DocumentoDeleteResponse(BaseModel):
    """Response después de eliminar."""
    success: bool
    chunks_eliminados: int


# ============================================
# Schemas para Consultas RAG
# ============================================

class RAGQueryRequest(BaseModel):
    """Request para consulta semántica."""
    
    universidad_id: UUID = Field(
        ...,
        description="ID de la universidad para filtrar resultados"
    )
    
    query: str = Field(
        ...,
        min_length=3,
        max_length=500,
        description="Pregunta del usuario"
    )
    
    tipos: Optional[List[str]] = Field(
        default=None,
        description="Filtrar por tipos de documento (opcional)"
    )
    
    top_k: int = Field(
        default=5,
        ge=1,
        le=20,
        description="Número máximo de resultados"
    )
    
    score_threshold: float = Field(
        default=0.5,
        ge=0.0,
        le=1.0,
        description="Umbral mínimo de similitud (0-1)"
    )
    
    include_metadata: bool = Field(
        default=True,
        description="Incluir metadatos en la respuesta"
    )
    
    model_config = {
        "json_schema_extra": {
            "example": {
                "universidad_id": "123e4567-e89b-12d3-a456-426614174000",
                "query": "¿Cuál es la fecha límite de inscripciones?",
                "tipos": ["calendario", "reglamento"],
                "top_k": 5
            }
        }
    }


class RAGResult(BaseModel):
    """Un resultado de búsqueda RAG."""
    
    id: UUID
    tipo: str
    titulo: str
    contenido: str
    score: float = Field(..., description="Similitud coseno (0-1)")
    metadata: Optional[Dict[str, Any]] = None
    source_url: Optional[str] = None


class RAGQueryResponse(BaseModel):
    """Response de consulta RAG."""
    
    success: bool
    query: str
    resultados: List[RAGResult]
    total_encontrados: int
    contexto_combinado: str = Field(
        ...,
        description="Todos los chunks relevantes concatenados para LLM"
    )
    tiempo_busqueda_ms: float


# ============================================
# Schemas para Respuesta Generada
# ============================================

class RAGAnswerRequest(BaseModel):
    """Request para generar respuesta con LLM usando contexto RAG."""
    
    universidad_id: UUID
    query: str = Field(..., min_length=3, max_length=500)
    tipos: Optional[List[str]] = None
    top_k: int = Field(default=5, ge=1, le=20)
    include_sources: bool = Field(
        default=True,
        description="Incluir fuentes en la respuesta"
    )


class SourceReference(BaseModel):
    """Referencia a fuente usada."""
    titulo: str
    tipo: str
    relevancia: float
    source_url: Optional[str] = None


class RAGAnswerResponse(BaseModel):
    """Response con respuesta generada por LLM."""
    
    success: bool
    query: str
    respuesta: str = Field(..., description="Respuesta generada por el LLM")
    fuentes: List[SourceReference] = Field(
        default=[],
        description="Documentos usados para generar la respuesta"
    )
    confianza: float = Field(
        ...,
        ge=0.0,
        le=1.0,
        description="Nivel de confianza basado en relevancia de fuentes"
    )
    advertencia: Optional[str] = Field(
        default=None,
        description="Advertencia si no hay suficiente contexto"
    )
    tiempo_total_ms: float


# ============================================
# Schemas para Listado/Admin
# ============================================

class UniversidadInfoOut(BaseModel):
    """Representación de un chunk para listados."""
    
    id: UUID
    tipo: str
    titulo: str
    contenido_preview: str
    tiene_embedding: bool
    metadata: Optional[Dict[str, Any]]
    source_url: Optional[str]
    created_at: datetime
    updated_at: datetime
    
    model_config = {"from_attributes": True}


class ListDocumentosRequest(BaseModel):
    """Request para listar documentos."""
    universidad_id: UUID
    tipo: Optional[str] = None
    limite: int = Field(default=50, ge=1, le=500)
    offset: int = Field(default=0, ge=0)


class ListDocumentosResponse(BaseModel):
    """Response con lista de documentos."""
    success: bool
    total: int
    documentos: List[UniversidadInfoOut]
    tipos_disponibles: List[str]


# ============================================
# Schemas para el Tool
# ============================================

class RAGToolInput(BaseModel):
    """Input para el RAG Tool de LangChain."""
    
    query: str = Field(
        ...,
        description="Pregunta del estudiante sobre la universidad"
    )
    
    tipos: Optional[List[str]] = Field(
        default=None,
        description=f"Filtrar por tipos: {', '.join(TIPOS_DOCUMENTO[:6])}..."
    )
    
    top_k: int = Field(
        default=5,
        description="Número de documentos a recuperar"
    )


class RAGToolOutput(BaseModel):
    """Output del RAG Tool."""
    
    success: bool
    respuesta: str
    fuentes: List[Dict[str, Any]]
    num_documentos_usados: int
    confianza: float
