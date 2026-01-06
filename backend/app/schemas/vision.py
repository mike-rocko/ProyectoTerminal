"""
Pydantic schemas para el servicio de visión.
"""
from typing import Any, Dict, List, Literal, Optional

from pydantic import BaseModel, Field


# ============================================================================
# SCHEMAS DE OFERTA ACADÉMICA
# ============================================================================
class HorarioMateria(BaseModel):
    """Horario de una materia."""
    dias: List[str] = Field(default_factory=list, description="Días de la semana")
    hora_inicio: Optional[str] = Field(None, description="Hora inicio (24hrs)")
    hora_fin: Optional[str] = Field(None, description="Hora fin (24hrs)")
    aula: Optional[str] = None


class MateriaOferta(BaseModel):
    """Materia extraída de la oferta académica."""
    nrc: Optional[str] = Field(None, description="Código único de sección")
    clave: Optional[str] = Field(None, description="Código de la materia")
    nombre: str = Field(..., description="Nombre de la materia")
    seccion: Optional[str] = None
    creditos: Optional[int] = None
    profesor: Optional[str] = None
    cupo: Optional[int] = None
    disponibles: Optional[int] = None
    horario: Optional[HorarioMateria] = None
    modalidad: Optional[str] = None


class OfertaAcademicaResponse(BaseModel):
    """Respuesta del análisis de oferta académica."""
    semestre: Optional[str] = None
    universidad: Optional[str] = None
    materias: List[MateriaOferta] = Field(default_factory=list)
    notas: Optional[str] = None


# ============================================================================
# SCHEMAS DE MAPA CURRICULAR
# ============================================================================
class MateriaMapaCurricular(BaseModel):
    """Materia en el mapa curricular."""
    clave: str
    nombre: str
    creditos: Optional[int] = None
    horas_teoria: Optional[int] = None
    horas_practica: Optional[int] = None
    tipo: Optional[str] = None
    prerrequisitos: List[str] = Field(default_factory=list)
    correquisitos: List[str] = Field(default_factory=list)


class SemestreMapa(BaseModel):
    """Semestre del mapa curricular."""
    numero: int
    materias: List[MateriaMapaCurricular] = Field(default_factory=list)


class AreaFormacion(BaseModel):
    """Área de formación del plan de estudios."""
    nombre: str
    creditos: Optional[int] = None
    color: Optional[str] = None


class MapaCurricularResponse(BaseModel):
    """Respuesta del análisis de mapa curricular."""
    carrera: Optional[str] = None
    plan: Optional[str] = None
    total_creditos: Optional[int] = None
    duracion_semestres: Optional[int] = None
    semestres: List[SemestreMapa] = Field(default_factory=list)
    areas_formacion: List[AreaFormacion] = Field(default_factory=list)
    notas: Optional[str] = None


# ============================================================================
# SCHEMAS DE KÁRDEX
# ============================================================================
class MateriaKardex(BaseModel):
    """Materia en el kárdex."""
    clave: Optional[str] = None
    nombre: str
    creditos: Optional[int] = None
    calificacion: Optional[float] = None
    calificacion_letra: Optional[str] = None
    estado: Optional[str] = None


class PeriodoKardex(BaseModel):
    """Periodo académico en el kárdex."""
    periodo: str
    materias: List[MateriaKardex] = Field(default_factory=list)
    creditos_periodo: Optional[int] = None
    promedio_periodo: Optional[float] = None


class EstudianteKardex(BaseModel):
    """Datos del estudiante en el kárdex."""
    nombre: Optional[str] = None
    matricula: Optional[str] = None
    carrera: Optional[str] = None
    plan: Optional[str] = None
    semestre_actual: Optional[int] = None
    promedio_general: Optional[float] = None


class ResumenKardex(BaseModel):
    """Resumen del avance académico."""
    creditos_aprobados: Optional[int] = None
    creditos_reprobados: Optional[int] = None
    creditos_totales_plan: Optional[int] = None
    porcentaje_avance: Optional[float] = None
    materias_reprobadas: List[str] = Field(default_factory=list)


class KardexResponse(BaseModel):
    """Respuesta del análisis de kárdex."""
    estudiante: Optional[EstudianteKardex] = None
    periodos: List[PeriodoKardex] = Field(default_factory=list)
    resumen: Optional[ResumenKardex] = None
    notas: Optional[str] = None


# ============================================================================
# SCHEMAS GENERALES DE VISION
# ============================================================================
class VisionAnalyzeRequest(BaseModel):
    """Request para analizar imagen (cuando se envía por URL o path)."""
    image_url: Optional[str] = Field(None, description="URL de la imagen")
    doc_type: Literal["oferta", "mapa", "kardex"] = Field(
        ..., description="Tipo de documento a analizar"
    )
    use_pro: bool = Field(
        False, description="Usar Gemini Pro (más lento pero más preciso)"
    )


class VisionMetadata(BaseModel):
    """Metadata del análisis."""
    doc_type: str
    model: Optional[str] = None
    image_size: Optional[str] = None
    image_format: Optional[str] = None
    # Para PDFs
    source: Optional[str] = None
    total_pages: Optional[int] = None
    pages_processed: Optional[int] = None


class VisionErrorResponse(BaseModel):
    """Respuesta de error del vision service."""
    error: bool = True
    message: str
    doc_type: Optional[str] = None


class VisionAnalyzeResponse(BaseModel):
    """Respuesta genérica del análisis (wrapper)."""
    success: bool
    doc_type: str
    data: Dict[str, Any]
    metadata: Optional[VisionMetadata] = None
    error: Optional[str] = None
