"""
Pydantic schemas para el Schedule Builder.

Define estructuras para:
- Bloques de tiempo y horarios
- Materias de la oferta académica
- Disponibilidad del estudiante
- Horarios generados y rankeados
"""
from datetime import time
from typing import Any, Dict, List, Literal, Optional
from pydantic import BaseModel, Field, field_validator


# ============================================================================
# TIPOS Y CONSTANTES
# ============================================================================
DiaSemana = Literal["Lunes", "Martes", "Miércoles", "Jueves", "Viernes", "Sábado"]

DIAS_ORDEN = {
    "Lunes": 0,
    "Martes": 1,
    "Miércoles": 2,
    "Jueves": 3,
    "Viernes": 4,
    "Sábado": 5
}


# ============================================================================
# BLOQUES DE TIEMPO
# ============================================================================
class BloqueHorario(BaseModel):
    """Un bloque de tiempo específico (ej: Lunes 9:00-11:00)."""
    dia: DiaSemana
    hora_inicio: str = Field(..., description="Hora inicio en formato HH:MM (24hrs)")
    hora_fin: str = Field(..., description="Hora fin en formato HH:MM (24hrs)")
    aula: Optional[str] = None
    
    @field_validator('hora_inicio', 'hora_fin')
    @classmethod
    def validar_formato_hora(cls, v: str) -> str:
        """Valida que la hora esté en formato HH:MM."""
        try:
            parts = v.split(':')
            hora = int(parts[0])
            minuto = int(parts[1]) if len(parts) > 1 else 0
            if not (0 <= hora <= 23 and 0 <= minuto <= 59):
                raise ValueError
            return f"{hora:02d}:{minuto:02d}"
        except (ValueError, IndexError):
            raise ValueError(f"Formato de hora inválido: {v}. Usar HH:MM")
    
    def inicio_minutos(self) -> int:
        """Convierte hora inicio a minutos desde medianoche."""
        h, m = map(int, self.hora_inicio.split(':'))
        return h * 60 + m
    
    def fin_minutos(self) -> int:
        """Convierte hora fin a minutos desde medianoche."""
        h, m = map(int, self.hora_fin.split(':'))
        return h * 60 + m
    
    def duracion_minutos(self) -> int:
        """Duración del bloque en minutos."""
        return self.fin_minutos() - self.inicio_minutos()
    
    def se_traslapa_con(self, otro: "BloqueHorario") -> bool:
        """Verifica si este bloque se traslapa con otro."""
        if self.dia != otro.dia:
            return False
        
        # Traslape: inicio1 < fin2 AND inicio2 < fin1
        return (self.inicio_minutos() < otro.fin_minutos() and 
                otro.inicio_minutos() < self.fin_minutos())


class DisponibilidadDia(BaseModel):
    """Bloques de disponibilidad para un día específico."""
    dia: DiaSemana
    bloques: List[BloqueHorario] = Field(default_factory=list)
    
    def esta_disponible(self, bloque: BloqueHorario) -> bool:
        """Verifica si un bloque cae dentro de la disponibilidad."""
        if bloque.dia != self.dia:
            return False
        
        for disponible in self.bloques:
            if (disponible.inicio_minutos() <= bloque.inicio_minutos() and
                bloque.fin_minutos() <= disponible.fin_minutos()):
                return True
        return False


# ============================================================================
# MATERIAS Y OFERTA ACADÉMICA
# ============================================================================
class MateriaOferta(BaseModel):
    """Una materia de la oferta académica con su horario."""
    nrc: str = Field(..., description="Código único de la sección")
    clave: str = Field(..., description="Código de la materia")
    nombre: str
    creditos: int = Field(default=6, ge=0)
    profesor: Optional[str] = None
    cupo_disponible: Optional[int] = None
    horarios: List[BloqueHorario] = Field(default_factory=list)
    modalidad: Optional[str] = None
    
    # Metadata para priorización
    es_reprobada: bool = Field(default=False, description="Si el estudiante la reprobó antes")
    es_prerrequisito_de: List[str] = Field(default_factory=list, description="Materias que desbloquea")
    prioridad: int = Field(default=0, description="Prioridad manual (mayor = más importante)")


class MateriaElegible(BaseModel):
    """Una materia que el estudiante puede cursar (cumple prerrequisitos)."""
    clave: str
    nombre: str
    creditos: int
    opciones: List[MateriaOferta] = Field(..., description="Secciones disponibles en oferta")
    es_reprobada: bool = False
    es_obligatoria: bool = True
    razon_elegible: Optional[str] = None


# ============================================================================
# DISPONIBILIDAD DEL ESTUDIANTE
# ============================================================================
class DisponibilidadEstudiante(BaseModel):
    """Disponibilidad semanal del estudiante."""
    dias: Dict[DiaSemana, List[BloqueHorario]] = Field(
        default_factory=dict,
        description="Bloques disponibles por día"
    )
    
    def esta_disponible(self, bloque: BloqueHorario) -> bool:
        """Verifica si un bloque cae en horario disponible."""
        if bloque.dia not in self.dias:
            return False
        
        for disponible in self.dias[bloque.dia]:
            if (disponible.inicio_minutos() <= bloque.inicio_minutos() and
                bloque.fin_minutos() <= disponible.fin_minutos()):
                return True
        return False
    
    def todos_disponibles(self, bloques: List[BloqueHorario]) -> bool:
        """Verifica si todos los bloques caen en horario disponible."""
        return all(self.esta_disponible(b) for b in bloques)


# ============================================================================
# HORARIOS GENERADOS
# ============================================================================
class HorarioGenerado(BaseModel):
    """Un horario completo generado (combinación de materias)."""
    materias: List[MateriaOferta] = Field(..., description="Materias incluidas")
    total_creditos: int = 0
    total_horas_semana: float = 0
    
    # Métricas de calidad
    score: float = Field(default=0, description="Puntuación general (0-100)")
    huecos_minutos: int = Field(default=0, description="Tiempo muerto entre clases")
    dias_con_clase: int = Field(default=0)
    hora_inicio_mas_temprana: Optional[str] = None
    hora_fin_mas_tardia: Optional[str] = None
    amplitud_horaria: int = Field(default=0, description="Minutos entre primera y última clase del día")
    
    # Prioridades
    materias_reprobadas_incluidas: int = 0
    materias_que_desbloquean: int = 0
    
    def calcular_metricas(self) -> None:
        """Calcula todas las métricas del horario."""
        if not self.materias:
            return
        
        self.total_creditos = sum(m.creditos for m in self.materias)
        
        # Recopilar todos los bloques
        todos_bloques: List[BloqueHorario] = []
        for materia in self.materias:
            todos_bloques.extend(materia.horarios)
        
        if not todos_bloques:
            return
        
        # Horas por semana
        minutos_totales = sum(b.duracion_minutos() for b in todos_bloques)
        self.total_horas_semana = minutos_totales / 60
        
        # Días con clase
        dias_unicos = set(b.dia for b in todos_bloques)
        self.dias_con_clase = len(dias_unicos)
        
        # Hora más temprana y tardía
        self.hora_inicio_mas_temprana = min(b.hora_inicio for b in todos_bloques)
        self.hora_fin_mas_tardia = max(b.hora_fin for b in todos_bloques)
        
        # Calcular huecos por día
        self._calcular_huecos(todos_bloques)
        
        # Materias prioritarias
        self.materias_reprobadas_incluidas = sum(1 for m in self.materias if m.es_reprobada)
        self.materias_que_desbloquean = sum(len(m.es_prerrequisito_de) for m in self.materias)
    
    def _calcular_huecos(self, bloques: List[BloqueHorario]) -> None:
        """Calcula los huecos (tiempo muerto) entre clases."""
        # Agrupar por día
        por_dia: Dict[str, List[BloqueHorario]] = {}
        for b in bloques:
            if b.dia not in por_dia:
                por_dia[b.dia] = []
            por_dia[b.dia].append(b)
        
        huecos_total = 0
        amplitud_total = 0
        
        for dia, bloques_dia in por_dia.items():
            # Ordenar por hora inicio
            bloques_dia.sort(key=lambda x: x.inicio_minutos())
            
            # Calcular huecos entre clases consecutivas
            for i in range(len(bloques_dia) - 1):
                fin_actual = bloques_dia[i].fin_minutos()
                inicio_siguiente = bloques_dia[i + 1].inicio_minutos()
                if inicio_siguiente > fin_actual:
                    huecos_total += (inicio_siguiente - fin_actual)
            
            # Amplitud del día
            if bloques_dia:
                amplitud = bloques_dia[-1].fin_minutos() - bloques_dia[0].inicio_minutos()
                amplitud_total += amplitud
        
        self.huecos_minutos = huecos_total
        self.amplitud_horaria = amplitud_total


class HorarioRankeado(BaseModel):
    """Horario con explicación de por qué se recomienda."""
    horario: HorarioGenerado
    ranking: int = Field(..., description="Posición en el ranking (1 = mejor)")
    explicacion: str = Field(..., description="Por qué se recomienda este horario")
    pros: List[str] = Field(default_factory=list)
    contras: List[str] = Field(default_factory=list)


# ============================================================================
# REQUESTS Y RESPONSES
# ============================================================================
class ScheduleGenerateRequest(BaseModel):
    """Request para generar horarios."""
    materias_elegibles: List[MateriaElegible] = Field(
        ..., description="Materias que el estudiante puede cursar"
    )
    disponibilidad: Optional[DisponibilidadEstudiante] = Field(
        None, description="Horarios en que el estudiante está disponible"
    )
    creditos_minimos: int = Field(default=12, ge=0)
    creditos_maximos: int = Field(default=24, le=36)
    max_materias: int = Field(default=6, ge=1, le=10)
    priorizar_reprobadas: bool = Field(default=True)
    evitar_huecos: bool = Field(default=True)
    max_resultados: int = Field(default=5, ge=1, le=20)


class ScheduleGenerateResponse(BaseModel):
    """Response con horarios generados."""
    success: bool
    total_generados: int
    horarios: List[HorarioRankeado]
    mensaje: Optional[str] = None
    advertencias: List[str] = Field(default_factory=list)
