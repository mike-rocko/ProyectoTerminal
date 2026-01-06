"""
Modelo para información de universidad (RAG).

Almacena chunks de documentos con embeddings vectoriales
para búsqueda semántica usando pgvector.
"""
from datetime import datetime
from typing import List, Optional
from uuid import uuid4

from pgvector.sqlalchemy import Vector
from sqlalchemy import Column, DateTime, ForeignKey, Index, String, Text, text
from sqlalchemy.dialects.postgresql import JSONB, UUID
from sqlalchemy.orm import relationship

from app.db.base import Base


class UniversidadInfo(Base):
    """Almacena información de la universidad para RAG.
    
    Cada registro es un "chunk" de un documento con su embedding
    para búsqueda semántica. Filtrado por universidad_id (multi-tenant).
    
    Attributes:
        id: UUID único del chunk
        universidad_id: FK a la universidad (multi-tenant)
        tipo: Tipo de documento (mision, vision, reglamento, calendario, faq, etc.)
        titulo: Título o nombre del documento fuente
        contenido: Texto del chunk
        embedding: Vector de 768 dims (Google embedding-001)
        metadata: Info adicional (página, sección, fecha, etc.)
        source_url: URL o path del documento original
        created_at: Timestamp de creación
        updated_at: Timestamp de última actualización
    """
    
    __tablename__ = "universidad_info"
    
    id = Column(
        UUID(as_uuid=True),
        primary_key=True,
        default=uuid4,
        server_default=text("gen_random_uuid()")
    )
    
    universidad_id = Column(
        UUID(as_uuid=True),
        ForeignKey("universidads.id", ondelete="CASCADE"),
        nullable=False,
        index=True
    )
    
    tipo = Column(
        String(50),
        nullable=False,
        index=True,
        comment="Tipo: mision, vision, reglamento, calendario, faq, contacto, tramite"
    )
    
    titulo = Column(
        String(255),
        nullable=False,
        comment="Título o nombre del documento fuente"
    )
    
    contenido = Column(
        Text,
        nullable=False,
        comment="Texto del chunk para búsqueda"
    )
    
    # Vector de 768 dimensiones (Google embedding-001)
    embedding = Column(
        Vector(768),
        nullable=True,
        comment="Embedding vectorial para búsqueda semántica"
    )
    
    extra_data = Column(
        "metadata",  # Nombre en DB, pero atributo Python diferente
        JSONB,
        nullable=True,
        default={},
        comment="Metadatos adicionales: página, sección, autor, fecha_doc"
    )
    
    source_url = Column(
        String(500),
        nullable=True,
        comment="URL o path del documento original"
    )
    
    created_at = Column(
        DateTime,
        nullable=False,
        default=datetime.utcnow,
        server_default=text("NOW()")
    )
    
    updated_at = Column(
        DateTime,
        nullable=False,
        default=datetime.utcnow,
        onupdate=datetime.utcnow,
        server_default=text("NOW()")
    )
    
    # Relación con Universidad
    universidad = relationship("Universidad", back_populates="info_chunks")
    
    # Índice para búsqueda vectorial con coseno
    # Usamos ivfflat para mejor performance en datasets grandes
    __table_args__ = (
        Index(
            "ix_universidad_info_embedding",
            embedding,
            postgresql_using="ivfflat",
            postgresql_with={"lists": 100},
            postgresql_ops={"embedding": "vector_cosine_ops"}
        ),
    )
    
    def __repr__(self) -> str:
        return f"<UniversidadInfo(id={self.id}, tipo={self.tipo}, titulo={self.titulo[:30]})>"


# Tipos válidos de documentos
TIPOS_DOCUMENTO = [
    "mision",      # Misión de la universidad
    "vision",      # Visión de la universidad
    "valores",     # Valores institucionales
    "reglamento",  # Reglamentos (inscripción, académico, etc.)
    "calendario",  # Calendario académico
    "tramite",     # Trámites y procedimientos
    "contacto",    # Información de contacto
    "faq",         # Preguntas frecuentes
    "carrera",     # Información de carreras
    "servicio",    # Servicios estudiantiles
    "beca",        # Información de becas
    "otro"         # Otro tipo de información
]
