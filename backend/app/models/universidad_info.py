"""
Modelo Universidad Info - Base de conocimiento para RAG
Almacena documentos e información de cada universidad
"""
from sqlalchemy import Column, String, TIMESTAMP, JSON, Enum, Text, ForeignKey, Index
from sqlalchemy.sql import func
from app.db.session import Base
from pgvector.sqlalchemy import Vector
import enum
import uuid


class TipoInfo(str, enum.Enum):
    """Tipos de información almacenada"""
    GENERAL = "general"           # Misión, visión, historia
    REGLAMENTO = "reglamento"     # Reglamentos académicos
    MATERIA = "materia"           # Detalles de materias
    ORGANIGRAMA = "organigrama"   # Estructura organizacional
    FAQ = "faq"                   # Preguntas frecuentes
    ENLACE = "enlace"             # Links a recursos externos
    CALENDARIO = "calendario"     # Calendario académico


class UniversidadInfo(Base):
    """Modelo de Información de Universidad (para RAG)"""
    __tablename__ = "universidad_info"
    
    # Primary Key
    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    
    # Foreign Key - Multi-tenant
    universidad_id = Column(String(36), ForeignKey("universidades.id"), nullable=False, index=True)
    
    # Clasificación
    tipo = Column(Enum(TipoInfo), nullable=False, index=True)
    categoria = Column(String(100))  # "academico", "administrativo", "servicios"
    
    # Contenido
    titulo = Column(String(500), nullable=False)
    contenido = Column(Text, nullable=False)  # Texto completo del documento
    
    # Enlaces (opcional)
    url = Column(String(500))  # Link externo si aplica
    archivo_url = Column(String(500))  # PDF/imagen original en GCS
    
    # Metadata adicional
    info_metadata = Column(JSON, default={})
    # {
    #   "keywords": ["inscripciones", "fechas", "calendario"],
    #   "fecha_documento": "2024-01-15",
    #   "autor": "Coordinación Académica",
    #   "pagina": 3
    # }
    
    # Vector Embedding (para búsqueda semántica)
    # Dimensión: 768 para Gemini embedding-001
    embedding = Column(Vector(768))
    
    # Metadata temporal
    created_at = Column(TIMESTAMP, server_default=func.now(), nullable=False)
    updated_at = Column(TIMESTAMP, server_default=func.now(), onupdate=func.now(), nullable=False)
    
    # Relaciones
    # universidad = relationship("Universidad", back_populates="info_documentos")
    
    def __repr__(self):
        return f"<UniversidadInfo(id={self.id}, tipo={self.tipo}, titulo={self.titulo[:30]}...)>"


# Índice para búsqueda vectorial eficiente
# Esto se crea después con Alembic:
# CREATE INDEX ON universidad_info USING ivfflat (embedding vector_cosine_ops) WITH (lists = 100);
