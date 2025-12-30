"""
Modelo Universidad - Multi-tenant principal
Cada universidad es un tenant aislado con su propia configuración
"""
from sqlalchemy import Column, String, TIMESTAMP, JSON, Boolean, Text
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from app.db.session import Base
import uuid


class Universidad(Base):
    """Modelo de Universidad (Tenant principal)"""
    __tablename__ = "universidades"
    
    # Primary Key
    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    
    # Información Básica
    nombre = Column(String(255), nullable=False, unique=True)
    slug = Column(String(100), nullable=False, unique=True, index=True)
    # Ej: "unicaribe" -> unicaribe.tutorai.com
    
    # Contacto
    email_contacto = Column(String(255), nullable=False)
    telefono = Column(String(50))
    direccion = Column(Text)
    sitio_web = Column(String(255))
    
    # Branding
    logo_url = Column(String(500))  # URL de Google Cloud Storage
    colores_tema = Column(JSON)  # {"primary": "#003366", "secondary": "#FF6B35"}
    
    # Configuración
    config = Column(JSON, default={})  # Configuraciones específicas
    # Ejemplo: {"max_creditos": 24, "usa_seriacion": true}
    
    # Estado
    activo = Column(Boolean, default=True, nullable=False)
    
    # Metadata
    created_at = Column(TIMESTAMP, server_default=func.now(), nullable=False)
    updated_at = Column(TIMESTAMP, server_default=func.now(), onupdate=func.now(), nullable=False)
    
    # Relaciones (se configuran después de crear otros modelos)
    # estudiantes = relationship("Estudiante", back_populates="universidad")
    # carreras = relationship("Carrera", back_populates="universidad")
    # info_documentos = relationship("UniversidadInfo", back_populates="universidad")
    
    def __repr__(self):
        return f"<Universidad(id={self.id}, nombre={self.nombre}, slug={self.slug})>"
