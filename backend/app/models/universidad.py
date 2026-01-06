"""
Modelo Universidad - Tenant principal del sistema multi-tenant.
Cada universidad tiene sus propios estudiantes, carreras e información.
"""
from sqlalchemy import Column, String, Text
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import relationship

from app.db.base import Base


class Universidad(Base):
    """
    Representa una universidad en el sistema.
    
    Cada universidad es un tenant separado con:
    - Su propia configuración (colores, logo)
    - Sus propias carreras
    - Sus propios estudiantes
    - Su propia información para RAG
    """
    
    # Información básica
    nombre = Column(String(255), nullable=False)
    slug = Column(String(100), unique=True, nullable=False, index=True)
    # Ejemplo: "unicaribe" -> unicaribe.tutorai.com
    
    # Branding
    logo_url = Column(String(500), nullable=True)
    
    # Configuración flexible (colores, features habilitados, etc.)
    config = Column(
        JSONB,
        default={
            "colores": {
                "primario": "#1E40AF",
                "secundario": "#3B82F6"
            },
            "features": {
                "chat_rag": True,
                "schedule_builder": True
            }
        },
        nullable=False
    )
    
    # Información de contacto
    email_contacto = Column(String(255), nullable=True)
    telefono = Column(String(50), nullable=True)
    direccion = Column(Text, nullable=True)
    
    # Relaciones
    carreras = relationship("Carrera", back_populates="universidad", cascade="all, delete-orphan")
    estudiantes = relationship("Estudiante", back_populates="universidad", cascade="all, delete-orphan")
    info_chunks = relationship("UniversidadInfo", back_populates="universidad", cascade="all, delete-orphan")
    
    def __repr__(self) -> str:
        return f"<Universidad {self.nombre} ({self.slug})>"
