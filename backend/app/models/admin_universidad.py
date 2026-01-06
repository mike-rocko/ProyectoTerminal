"""
Modelo AdminUniversidad - Administradores de cada universidad.
"""
from sqlalchemy import Column, String, Boolean, ForeignKey
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
import uuid

from app.db.base import Base


class AdminUniversidad(Base):
    """
    Representa un administrador de universidad.
    
    Puede gestionar:
    - Información de la universidad
    - Carreras y mapas curriculares
    - Documentos para RAG
    """
    
    __tablename__ = "admins_universidad"
    
    # Relación con universidad
    universidad_id = Column(
        UUID(as_uuid=True),
        ForeignKey("universidads.id", ondelete="CASCADE"),
        nullable=False,
        index=True
    )
    
    # Información del admin
    email = Column(String(255), unique=True, nullable=False, index=True)
    password_hash = Column(String(255), nullable=False)
    nombre = Column(String(255), nullable=False)
    
    # Estado
    is_active = Column(Boolean, default=True, nullable=False)
    is_super_admin = Column(Boolean, default=False, nullable=False)  # Admin principal
    
    # Relaciones
    universidad = relationship("Universidad", backref="admins")
