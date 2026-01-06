"""
Schemas para Universidad.
"""
from typing import Optional
from uuid import UUID

from pydantic import BaseModel, Field

from app.schemas.base import BaseSchema, TimestampMixin, IDMixin


# ============================================
# Request Schemas
# ============================================

class UniversidadCreate(BaseModel):
    """Schema para crear una universidad."""
    nombre: str = Field(..., min_length=3, max_length=255, examples=["Universidad del Caribe"])
    slug: str = Field(..., min_length=3, max_length=100, pattern=r"^[a-z0-9-]+$", examples=["unicaribe"])
    logo_url: Optional[str] = Field(None, max_length=500)
    email_contacto: Optional[str] = Field(None, max_length=255)
    telefono: Optional[str] = Field(None, max_length=50)
    direccion: Optional[str] = None
    config: Optional[dict] = None


class UniversidadUpdate(BaseModel):
    """Schema para actualizar una universidad."""
    nombre: Optional[str] = Field(None, min_length=3, max_length=255)
    logo_url: Optional[str] = Field(None, max_length=500)
    email_contacto: Optional[str] = Field(None, max_length=255)
    telefono: Optional[str] = Field(None, max_length=50)
    direccion: Optional[str] = None
    config: Optional[dict] = None


# ============================================
# Response Schemas
# ============================================

class UniversidadResponse(BaseSchema, IDMixin, TimestampMixin):
    """Schema de respuesta para universidad."""
    nombre: str
    slug: str
    logo_url: Optional[str] = None
    email_contacto: Optional[str] = None
    telefono: Optional[str] = None
    direccion: Optional[str] = None
    config: dict = {}


class UniversidadListResponse(BaseSchema):
    """Schema para lista de universidades."""
    items: list[UniversidadResponse]
    total: int
