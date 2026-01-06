"""
Schemas para SesionConsultoria.
"""
from typing import Optional, Literal
from uuid import UUID
from datetime import datetime

from pydantic import BaseModel, Field

from app.schemas.base import BaseSchema, TimestampMixin, IDMixin


# ============================================
# Request Schemas
# ============================================

class SesionCreate(BaseModel):
    """Schema para iniciar una sesión de consultoría."""
    tipo: Literal["horario", "materias", "combinado", "chat"] = "combinado"


class DisponibilidadUpdate(BaseModel):
    """Schema para actualizar disponibilidad."""
    disponibilidad: dict = Field(
        ...,
        examples=[{
            "lunes": ["09:00-11:00", "14:00-18:00"],
            "martes": ["09:00-15:00"],
            "miercoles": ["09:00-18:00"],
            "jueves": ["09:00-11:00"],
            "viernes": ["09:00-13:00"]
        }]
    )


class FeedbackRequest(BaseModel):
    """Schema para feedback del estudiante."""
    calificacion: Literal["1", "2", "3", "4", "5"]
    comentario: Optional[str] = None


# ============================================
# Response Schemas
# ============================================

class SesionResponse(BaseSchema, IDMixin, TimestampMixin):
    """Schema de respuesta para sesión."""
    estudiante_id: UUID
    tipo: str
    estado: str
    img_oferta_url: Optional[str] = None
    img_mapa_url: Optional[str] = None
    img_kardex_url: Optional[str] = None
    disponibilidad: Optional[dict] = None
    calificacion: Optional[str] = None


class SesionDetalleResponse(SesionResponse):
    """Schema de respuesta con datos extraídos y recomendación."""
    oferta_data: Optional[dict] = None
    mapa_data: Optional[dict] = None
    kardex_data: Optional[dict] = None
    recomendacion: Optional[dict] = None
    explicacion: Optional[str] = None


class SesionListResponse(BaseSchema):
    """Schema para lista de sesiones."""
    items: list[SesionResponse]
    total: int


# ============================================
# Schemas para datos extraídos
# ============================================

class MateriaOferta(BaseModel):
    """Materia extraída de la oferta académica."""
    nrc: str
    nombre: str
    creditos: int
    profesor: Optional[str] = None
    horario: dict  # {"lunes": ["09:00-11:00"], ...}
    cupo: Optional[int] = None
    disponible: Optional[int] = None


class OfertaData(BaseModel):
    """Datos extraídos de la imagen de oferta."""
    semestre: str
    materias: list[MateriaOferta]


class MateriaKardex(BaseModel):
    """Materia del historial académico."""
    clave: str
    nombre: str
    creditos: int
    calificacion: Optional[float] = None
    estado: Literal["aprobada", "reprobada", "cursando", "pendiente"]
    semestre_cursado: Optional[str] = None


class KardexData(BaseModel):
    """Datos extraídos del kardex."""
    promedio_general: Optional[float] = None
    creditos_acumulados: int
    materias: list[MateriaKardex]


class HorarioRecomendado(BaseModel):
    """Un horario recomendado."""
    ranking: int
    materias: list[dict]
    total_creditos: int
    metricas: dict  # {"huecos": 0, "amplitud": "9-15", ...}


class RecomendacionData(BaseModel):
    """Resultado de la consultoría."""
    horarios: list[HorarioRecomendado]
    materias_elegibles: list[dict]
    advertencias: Optional[list[str]] = None
