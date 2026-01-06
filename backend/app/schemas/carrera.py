"""
Schemas para Carrera.
"""
from typing import Optional
from uuid import UUID

from pydantic import BaseModel, Field

from app.schemas.base import BaseSchema, TimestampMixin, IDMixin


# ============================================
# Request Schemas
# ============================================

class CarreraCreate(BaseModel):
    """Schema para crear una carrera."""
    nombre: str = Field(..., min_length=3, max_length=255, examples=["Ingeniería en Software"])
    clave: str = Field(..., min_length=2, max_length=50, examples=["ISW"])
    descripcion: Optional[str] = None
    total_creditos: Optional[str] = Field(None, max_length=10)
    duracion_semestres: Optional[str] = Field(None, max_length=10)
    plan_estudios: Optional[dict] = None


class CarreraUpdate(BaseModel):
    """Schema para actualizar una carrera."""
    nombre: Optional[str] = Field(None, min_length=3, max_length=255)
    descripcion: Optional[str] = None
    total_creditos: Optional[str] = Field(None, max_length=10)
    duracion_semestres: Optional[str] = Field(None, max_length=10)
    plan_estudios: Optional[dict] = None


# ============================================
# Response Schemas
# ============================================

class CarreraResponse(BaseSchema, IDMixin, TimestampMixin):
    """Schema de respuesta para carrera."""
    universidad_id: UUID
    nombre: str
    clave: str
    descripcion: Optional[str] = None
    total_creditos: Optional[str] = None
    duracion_semestres: Optional[str] = None
    plan_estudios: dict = {}


class CarreraListResponse(BaseSchema):
    """Schema para lista de carreras."""
    items: list[CarreraResponse]
    total: int
