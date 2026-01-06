"""
Schemas para Estudiante.
"""
from typing import Optional
from uuid import UUID

from pydantic import BaseModel, Field, EmailStr

from app.schemas.base import BaseSchema, TimestampMixin, IDMixin


# ============================================
# Request Schemas
# ============================================

class EstudianteCreate(BaseModel):
    """Schema para crear un estudiante (interno, usado por register)."""
    universidad_id: UUID
    matricula: str = Field(..., min_length=5, max_length=50)
    email: EmailStr
    password: str = Field(..., min_length=8)
    nombre: Optional[str] = Field(None, max_length=100)
    apellido: Optional[str] = Field(None, max_length=100)
    carrera_id: Optional[UUID] = None


class EstudianteUpdate(BaseModel):
    """Schema para actualizar un estudiante."""
    nombre: Optional[str] = Field(None, max_length=100)
    apellido: Optional[str] = Field(None, max_length=100)
    carrera_id: Optional[UUID] = None
    preferencias: Optional[dict] = None


# ============================================
# Response Schemas
# ============================================

class EstudianteResponse(BaseSchema, IDMixin, TimestampMixin):
    """Schema de respuesta para estudiante (sin password)."""
    universidad_id: UUID
    carrera_id: Optional[UUID] = None
    matricula: str
    email: str
    nombre: Optional[str] = None
    apellido: Optional[str] = None
    is_active: bool
    is_verified: bool
    preferencias: dict = {}


class EstudianteProfileResponse(EstudianteResponse):
    """Schema extendido con info de carrera."""
    carrera_nombre: Optional[str] = None
    universidad_nombre: Optional[str] = None
