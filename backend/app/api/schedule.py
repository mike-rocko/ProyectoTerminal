"""
Endpoints para generación de horarios académicos.

POST /api/v1/schedule/generate - Genera horarios optimizados
"""
import logging
from datetime import datetime
from typing import Any, Dict, List, Optional

from fastapi import APIRouter, HTTPException, status
from pydantic import BaseModel, Field

from app.schemas.schedule import (
    ScheduleGenerateRequest,
    ScheduleGenerateResponse,
    BloqueHorario,
    DisponibilidadEstudiante,
    MateriaElegible,
    MateriaOferta,
)
from app.services.schedule_service import get_schedule_service

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/schedule", tags=["Schedule Builder"])


# ============================================
# Helper functions
# ============================================

def _normalizar_dia(dia: str) -> str:
    """Normaliza el nombre del día para comparación."""
    dia_lower = dia.lower().strip()
    # Mapear variantes comunes
    mapping = {
        "lunes": "lunes", "lun": "lunes", "l": "lunes",
        "martes": "martes", "mar": "martes", "m": "martes",
        "miercoles": "miercoles", "miércoles": "miercoles", "mie": "miercoles", "mi": "miercoles",
        "jueves": "jueves", "jue": "jueves", "j": "jueves",
        "viernes": "viernes", "vie": "viernes", "v": "viernes",
        "sabado": "sabado", "sábado": "sabado", "sab": "sabado", "s": "sabado",
        "domingo": "domingo", "dom": "domingo", "d": "domingo",
    }
    return mapping.get(dia_lower, dia_lower)


def _hora_a_minutos(hora: str) -> int:
    """Convierte hora HH:MM a minutos desde medianoche."""
    try:
        partes = hora.strip().split(":")
        return int(partes[0]) * 60 + int(partes[1])
    except:
        return 0


def _horarios_conflictan(
    dia1: str, inicio1: str, fin1: str,
    dia2: str, inicio2: str, fin2: str
) -> bool:
    """
    Verifica si dos bloques de horario se traslapan.
    
    Retorna True si hay conflicto (traslape).
    """
    # Primero verificar si son el mismo día
    if _normalizar_dia(dia1) != _normalizar_dia(dia2):
        return False
    
    # Convertir horas a minutos para comparación fácil
    inicio1_min = _hora_a_minutos(inicio1)
    fin1_min = _hora_a_minutos(fin1)
    inicio2_min = _hora_a_minutos(inicio2)
    fin2_min = _hora_a_minutos(fin2)
    
    # Verificar traslape: NO hay traslape si uno termina antes que el otro empiece
    # Hay traslape si: NO (fin1 <= inicio2 OR fin2 <= inicio1)
    return not (fin1_min <= inicio2_min or fin2_min <= inicio1_min)


# ============================================
# Modelos simplificados para el API
# ============================================

class HorarioInput(BaseModel):
    """Bloque de horario simplificado para entrada."""
    dia: str = Field(..., description="Día de la semana: Lunes, Martes, etc.")
    hora_inicio: str = Field(..., description="Hora inicio en formato HH:MM (24hrs)")
    hora_fin: str = Field(..., description="Hora fin en formato HH:MM")
    aula: Optional[str] = Field(None, description="Aula o edificio")


class SeccionInput(BaseModel):
    """Sección/NRC de una materia en la oferta."""
    nrc: str = Field(..., description="NRC único de la sección")
    clave: str = Field(..., description="Clave de la materia")
    nombre: str = Field(..., description="Nombre de la materia")
    creditos: int = Field(..., ge=1, le=12)
    profesor: Optional[str] = None
    cupo_disponible: Optional[int] = None
    horarios: List[HorarioInput] = Field(..., min_length=1)
    modalidad: Optional[str] = None


class MateriaElegibleInput(BaseModel):
    """Materia que el estudiante puede cursar con sus opciones."""
    clave: str = Field(..., description="Clave de la materia")
    nombre: str = Field(..., description="Nombre de la materia")
    creditos: int = Field(..., ge=1, le=12)
    opciones: List[SeccionInput] = Field(..., description="Secciones disponibles")
    es_reprobada: bool = Field(default=False, description="Si el estudiante la reprobó")
    es_obligatoria: bool = Field(default=True, description="Si es materia obligatoria")


class BloqueDisponibilidadInput(BaseModel):
    """Bloque de disponibilidad del estudiante."""
    hora_inicio: str = Field(..., description="Hora inicio disponible HH:MM")
    hora_fin: str = Field(..., description="Hora fin disponible HH:MM")


class DisponibilidadInput(BaseModel):
    """Disponibilidad semanal del estudiante."""
    lunes: Optional[List[BloqueDisponibilidadInput]] = None
    martes: Optional[List[BloqueDisponibilidadInput]] = None
    miercoles: Optional[List[BloqueDisponibilidadInput]] = None
    jueves: Optional[List[BloqueDisponibilidadInput]] = None
    viernes: Optional[List[BloqueDisponibilidadInput]] = None
    sabado: Optional[List[BloqueDisponibilidadInput]] = None


class GenerateScheduleRequest(BaseModel):
    """Request para generar horarios desde API."""
    materias_elegibles: List[MateriaElegibleInput] = Field(
        ...,
        description="Materias que puede cursar con secciones disponibles"
    )
    disponibilidad: Optional[DisponibilidadInput] = Field(
        None,
        description="Horarios disponibles del estudiante por día"
    )
    creditos_minimos: int = Field(default=12, ge=6, le=30)
    creditos_maximos: int = Field(default=24, ge=6, le=36)
    max_materias: int = Field(default=6, ge=1, le=10)
    priorizar_reprobadas: bool = Field(default=True)
    evitar_huecos: bool = Field(default=True)
    max_resultados: int = Field(default=3, ge=1, le=10)
    
    model_config = {
        "json_schema_extra": {
            "example": {
                "materias_elegibles": [
                    {
                        "clave": "MAT201",
                        "nombre": "Cálculo Diferencial",
                        "creditos": 8,
                        "es_reprobada": False,
                        "es_obligatoria": True,
                        "opciones": [
                            {
                                "nrc": "10001",
                                "clave": "MAT201",
                                "nombre": "Cálculo Diferencial",
                                "creditos": 8,
                                "profesor": "Dr. García",
                                "horarios": [
                                    {"dia": "Lunes", "hora_inicio": "09:00", "hora_fin": "11:00"},
                                    {"dia": "Miércoles", "hora_inicio": "09:00", "hora_fin": "11:00"}
                                ]
                            }
                        ]
                    }
                ],
                "creditos_minimos": 12,
                "creditos_maximos": 24,
                "max_materias": 5,
                "max_resultados": 3
            }
        }
    }


class MateriaEnHorario(BaseModel):
    """Materia incluida en un horario generado."""
    nrc: str
    clave: str
    nombre: str
    creditos: int
    profesor: Optional[str] = None
    es_reprobada: bool = False
    horarios: List[HorarioInput]


class HorarioGeneradoOutput(BaseModel):
    """Horario generado con ranking y explicación."""
    ranking: int = Field(..., description="Posición en el ranking (1 = mejor)")
    score: float = Field(..., description="Puntuación 0-100")
    total_creditos: int
    total_materias: int
    total_horas_semana: float
    dias_con_clase: int
    huecos_minutos: int
    hora_inicio_mas_temprana: str
    hora_fin_mas_tardia: str
    materias: List[MateriaEnHorario]
    explicacion: str = Field(..., description="Explicación en lenguaje natural")
    pros: List[str]
    contras: List[str]


class GenerateScheduleResponse(BaseModel):
    """Response con horarios generados."""
    success: bool
    total_generados: int
    mensaje: str
    advertencias: List[str] = []
    horarios: List[HorarioGeneradoOutput]


def _convert_to_internal_request(
    req: GenerateScheduleRequest
) -> ScheduleGenerateRequest:
    """Convierte request del API a modelo interno."""
    
    # Convertir materias elegibles
    materias = []
    for m in req.materias_elegibles:
        opciones = []
        for opc in m.opciones:
            horarios = [
                BloqueHorario(
                    dia=h.dia,
                    hora_inicio=h.hora_inicio,
                    hora_fin=h.hora_fin,
                    aula=h.aula
                )
                for h in opc.horarios
            ]
            mat_oferta = MateriaOferta(
                nrc=opc.nrc,
                clave=opc.clave,
                nombre=opc.nombre,
                creditos=opc.creditos,
                profesor=opc.profesor,
                cupo_disponible=opc.cupo_disponible,
                horarios=horarios,
                modalidad=opc.modalidad
            )
            opciones.append(mat_oferta)
        
        elegible = MateriaElegible(
            clave=m.clave,
            nombre=m.nombre,
            creditos=m.creditos,
            opciones=opciones,
            es_reprobada=m.es_reprobada,
            es_obligatoria=m.es_obligatoria
        )
        materias.append(elegible)
    
    # Convertir disponibilidad
    disponibilidad = None
    if req.disponibilidad:
        dias: Dict[str, List[BloqueHorario]] = {}
        dia_mapping = {
            "lunes": "Lunes",
            "martes": "Martes", 
            "miercoles": "Miércoles",
            "jueves": "Jueves",
            "viernes": "Viernes",
            "sabado": "Sábado"
        }
        
        disp_dict = req.disponibilidad.model_dump(exclude_none=True)
        for dia_key, dia_nombre in dia_mapping.items():
            if dia_key in disp_dict and disp_dict[dia_key]:
                bloques = [
                    BloqueHorario(
                        dia=dia_nombre,
                        hora_inicio=b["hora_inicio"],
                        hora_fin=b["hora_fin"]
                    )
                    for b in disp_dict[dia_key]
                ]
                dias[dia_nombre] = bloques
        
        if dias:
            disponibilidad = DisponibilidadEstudiante(dias=dias)
    
    return ScheduleGenerateRequest(
        materias_elegibles=materias,
        disponibilidad=disponibilidad,
        creditos_minimos=req.creditos_minimos,
        creditos_maximos=req.creditos_maximos,
        max_materias=req.max_materias,
        priorizar_reprobadas=req.priorizar_reprobadas,
        evitar_huecos=req.evitar_huecos,
        max_resultados=req.max_resultados
    )


def _convert_to_api_response(
    internal: ScheduleGenerateResponse
) -> GenerateScheduleResponse:
    """Convierte response interno a modelo del API."""
    
    horarios_output = []
    for hr in internal.horarios:
        materias = []
        for mat in hr.horario.materias:
            horarios_mat = [
                HorarioInput(
                    dia=h.dia,
                    hora_inicio=h.hora_inicio,
                    hora_fin=h.hora_fin,
                    aula=h.aula
                )
                for h in mat.horarios
            ]
            materias.append(MateriaEnHorario(
                nrc=mat.nrc,
                clave=mat.clave,
                nombre=mat.nombre,
                creditos=mat.creditos,
                profesor=mat.profesor,
                es_reprobada=mat.es_reprobada,
                horarios=horarios_mat
            ))
        
        horario_out = HorarioGeneradoOutput(
            ranking=hr.ranking,
            score=hr.horario.score,
            total_creditos=hr.horario.total_creditos,
            total_materias=len(hr.horario.materias),
            total_horas_semana=hr.horario.total_horas_semana,
            dias_con_clase=hr.horario.dias_con_clase,
            huecos_minutos=hr.horario.huecos_minutos,
            hora_inicio_mas_temprana=hr.horario.hora_inicio_mas_temprana,
            hora_fin_mas_tardia=hr.horario.hora_fin_mas_tardia,
            materias=materias,
            explicacion=hr.explicacion,
            pros=hr.pros,
            contras=hr.contras
        )
        horarios_output.append(horario_out)
    
    return GenerateScheduleResponse(
        success=internal.success,
        total_generados=internal.total_generados,
        mensaje=internal.mensaje,
        advertencias=internal.advertencias,
        horarios=horarios_output
    )


@router.post(
    "/generate",
    response_model=GenerateScheduleResponse,
    summary="Generar horarios optimizados",
    description="""
    Genera combinaciones de horarios académicos optimizados basados en:
    - Materias elegibles del estudiante (filtradas por prerrequisitos)
    - Horarios de las secciones disponibles
    - Disponibilidad del estudiante (opcional)
    - Restricciones de créditos y materias
    
    El algoritmo:
    1. Genera todas las combinaciones válidas sin conflictos de horario
    2. Filtra por disponibilidad del estudiante
    3. Filtra por restricciones de créditos
    4. Rankea por: materias reprobadas, menos huecos, compactibilidad
    5. Retorna los mejores N horarios con explicaciones
    """
)
async def generate_schedule(
    request: GenerateScheduleRequest
) -> GenerateScheduleResponse:
    """Genera horarios académicos optimizados."""
    
    try:
        logger.info(f"Generando horarios para {len(request.materias_elegibles)} materias elegibles")
        
        # Validar que hay materias
        if not request.materias_elegibles:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Se requiere al menos una materia elegible"
            )
        
        # Validar que cada materia tiene al menos una opción
        for mat in request.materias_elegibles:
            if not mat.opciones:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail=f"La materia {mat.clave} no tiene secciones disponibles"
                )
        
        # Convertir a modelo interno
        internal_request = _convert_to_internal_request(request)
        
        # Generar horarios
        service = get_schedule_service()
        internal_response = service.generar_horarios(internal_request)
        
        # Convertir a modelo de salida
        api_response = _convert_to_api_response(internal_response)
        
        logger.info(f"Generados {api_response.total_generados} horarios, retornando {len(api_response.horarios)}")
        
        return api_response
        
    except HTTPException:
        raise
    except Exception as e:
        logger.exception(f"Error generando horarios: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error generando horarios: {str(e)}"
        )


@router.post(
    "/generate-test",
    response_model=GenerateScheduleResponse,
    summary="Prueba con datos de ejemplo",
    description="Genera horarios con datos de prueba predefinidos"
)
async def generate_schedule_test() -> GenerateScheduleResponse:
    """Genera horarios con datos de prueba."""
    
    # Datos de ejemplo que simulan un escenario real
    test_request = GenerateScheduleRequest(
        materias_elegibles=[
            # Materia reprobada (prioridad alta)
            MateriaElegibleInput(
                clave="MAT201",
                nombre="Cálculo Diferencial",
                creditos=8,
                es_reprobada=True,
                es_obligatoria=True,
                opciones=[
                    SeccionInput(
                        nrc="10001",
                        clave="MAT201",
                        nombre="Cálculo Diferencial",
                        creditos=8,
                        profesor="Dr. García",
                        horarios=[
                            HorarioInput(dia="Lunes", hora_inicio="09:00", hora_fin="11:00"),
                            HorarioInput(dia="Miércoles", hora_inicio="09:00", hora_fin="11:00"),
                        ]
                    ),
                    SeccionInput(
                        nrc="10002",
                        clave="MAT201",
                        nombre="Cálculo Diferencial",
                        creditos=8,
                        profesor="Dra. López",
                        horarios=[
                            HorarioInput(dia="Martes", hora_inicio="14:00", hora_fin="16:00"),
                            HorarioInput(dia="Jueves", hora_inicio="14:00", hora_fin="16:00"),
                        ]
                    ),
                ]
            ),
            # Programación
            MateriaElegibleInput(
                clave="PRG301",
                nombre="Programación Avanzada",
                creditos=6,
                es_reprobada=False,
                es_obligatoria=True,
                opciones=[
                    SeccionInput(
                        nrc="20001",
                        clave="PRG301",
                        nombre="Programación Avanzada",
                        creditos=6,
                        profesor="Ing. Martínez",
                        horarios=[
                            HorarioInput(dia="Lunes", hora_inicio="11:00", hora_fin="13:00"),
                            HorarioInput(dia="Miércoles", hora_inicio="11:00", hora_fin="13:00"),
                        ]
                    ),
                ]
            ),
            # Base de datos
            MateriaElegibleInput(
                clave="BD201",
                nombre="Bases de Datos",
                creditos=6,
                es_reprobada=False,
                es_obligatoria=True,
                opciones=[
                    SeccionInput(
                        nrc="30001",
                        clave="BD201",
                        nombre="Bases de Datos",
                        creditos=6,
                        profesor="Dr. Sánchez",
                        horarios=[
                            HorarioInput(dia="Martes", hora_inicio="09:00", hora_fin="11:00"),
                            HorarioInput(dia="Jueves", hora_inicio="09:00", hora_fin="11:00"),
                        ]
                    ),
                    SeccionInput(
                        nrc="30002",
                        clave="BD201",
                        nombre="Bases de Datos",
                        creditos=6,
                        profesor="Dra. Rodríguez",
                        horarios=[
                            HorarioInput(dia="Viernes", hora_inicio="09:00", hora_fin="12:00"),
                        ]
                    ),
                ]
            ),
            # Inglés
            MateriaElegibleInput(
                clave="ING301",
                nombre="Inglés V",
                creditos=4,
                es_reprobada=False,
                es_obligatoria=True,
                opciones=[
                    SeccionInput(
                        nrc="40001",
                        clave="ING301",
                        nombre="Inglés V",
                        creditos=4,
                        profesor="Prof. Smith",
                        horarios=[
                            HorarioInput(dia="Martes", hora_inicio="11:00", hora_fin="13:00"),
                        ]
                    ),
                    SeccionInput(
                        nrc="40002",
                        clave="ING301",
                        nombre="Inglés V",
                        creditos=4,
                        profesor="Prof. Johnson",
                        horarios=[
                            HorarioInput(dia="Jueves", hora_inicio="11:00", hora_fin="13:00"),
                        ]
                    ),
                ]
            ),
        ],
        creditos_minimos=12,
        creditos_maximos=24,
        max_materias=5,
        priorizar_reprobadas=True,
        evitar_huecos=True,
        max_resultados=3
    )
    
    return await generate_schedule(test_request)


# ============================================
# Endpoint para extraer bloques horarios de la oferta
# ============================================

class BloqueHorarioInfo(BaseModel):
    """Información de un bloque horario único."""
    dia: str
    hora_inicio: str
    hora_fin: str
    materias_en_bloque: int = Field(..., description="Número de materias/secciones en este horario")


class ExtractBloquesRequest(BaseModel):
    """Request para extraer bloques horarios."""
    oferta_data: Dict[str, Any] = Field(..., description="JSON extraído de la oferta por Vision API")


class ExtractBloquesResponse(BaseModel):
    """Response con bloques horarios únicos."""
    total_bloques: int
    bloques: List[BloqueHorarioInfo]
    dias_con_clases: List[str]
    hora_mas_temprana: str
    hora_mas_tardia: str


@router.post(
    "/extract-bloques",
    response_model=ExtractBloquesResponse,
    summary="Extrae bloques horarios únicos de la oferta",
    description="""
    Analiza la oferta académica y extrae todos los bloques horarios únicos.
    
    Útil para mostrar al estudiante qué horarios existen en la oferta
    y permitirle marcar cuáles NO puede tomar (conflictos).
    """
)
async def extract_bloques(request: ExtractBloquesRequest) -> ExtractBloquesResponse:
    """Extrae bloques horarios únicos de la oferta."""
    
    materias = request.oferta_data.get("materias", [])
    
    # Dict para contar materias por bloque: (dia, inicio, fin) -> count
    bloques_count: Dict[tuple, int] = {}
    todas_horas = []
    todos_dias = set()
    
    for materia in materias:
        horarios_raw = materia.get("horarios", materia.get("horario", []))
        
        if isinstance(horarios_raw, dict):
            horarios_raw = [horarios_raw]
        elif not isinstance(horarios_raw, list):
            continue
        
        for h in horarios_raw:
            if not isinstance(h, dict):
                continue
                
            dia = h.get("dia", "")
            inicio = h.get("hora_inicio", h.get("inicio", ""))
            fin = h.get("hora_fin", h.get("fin", ""))
            
            if dia and inicio and fin:
                key = (dia, inicio, fin)
                bloques_count[key] = bloques_count.get(key, 0) + 1
                todos_dias.add(dia)
                todas_horas.append(inicio)
                todas_horas.append(fin)
    
    # Ordenar días de la semana
    orden_dias = ["Lunes", "Martes", "Miércoles", "Jueves", "Viernes", "Sábado", "Domingo"]
    dias_ordenados = sorted(
        list(todos_dias),
        key=lambda d: orden_dias.index(d) if d in orden_dias else 99
    )
    
    # Construir lista de bloques ordenada
    bloques = []
    for (dia, inicio, fin), count in sorted(
        bloques_count.items(),
        key=lambda x: (orden_dias.index(x[0][0]) if x[0][0] in orden_dias else 99, x[0][1])
    ):
        bloques.append(BloqueHorarioInfo(
            dia=dia,
            hora_inicio=inicio,
            hora_fin=fin,
            materias_en_bloque=count
        ))
    
    # Encontrar hora más temprana y más tardía
    hora_temprana = min(todas_horas, default="07:00")
    hora_tardia = max(todas_horas, default="21:00")
    
    return ExtractBloquesResponse(
        total_bloques=len(bloques),
        bloques=bloques,
        dias_con_clases=dias_ordenados,
        hora_mas_temprana=hora_temprana,
        hora_mas_tardia=hora_tardia
    )


# ============================================
# Endpoint de Flujo Completo Vision → Schedule
# ============================================

class BloqueConflicto(BaseModel):
    """Bloque de horario donde el estudiante NO puede asistir."""
    dia: str = Field(..., description="Día de la semana")
    hora_inicio: str = Field(..., description="Hora inicio del conflicto HH:MM")
    hora_fin: str = Field(..., description="Hora fin del conflicto HH:MM")
    motivo: Optional[str] = Field(None, description="Razón del conflicto (trabajo, otro curso, etc.)")


class VisionToScheduleRequest(BaseModel):
    """
    Request para generar horarios a partir de datos extraídos por Vision.
    
    Recibe los JSONs extraídos del kárdex y la oferta académica,
    y genera horarios optimizados automáticamente.
    """
    kardex_data: Dict[str, Any] = Field(..., description="JSON extraído del kárdex por Vision API")
    oferta_data: Dict[str, Any] = Field(..., description="JSON extraído de la oferta por Vision API")
    mapa_data: Optional[Dict[str, Any]] = Field(None, description="JSON del mapa curricular (opcional)")
    
    # Configuración
    creditos_minimos: int = Field(default=12, ge=1, le=36)
    creditos_maximos: int = Field(default=24, ge=1, le=36)
    max_materias: int = Field(default=6, ge=1, le=10)
    priorizar_reprobadas: bool = Field(default=True)
    max_resultados: int = Field(default=3, ge=1, le=10)
    
    # Disponibilidad (opcional - horas DISPONIBLES)
    disponibilidad: Optional[Dict[str, List[Dict[str, str]]]] = Field(
        None, 
        description="Disponibilidad por día: {'Lunes': [{'hora_inicio': '09:00', 'hora_fin': '17:00'}]}"
    )
    
    # Conflictos (opcional - horas NO DISPONIBLES)
    conflictos: Optional[List[BloqueConflicto]] = Field(
        None,
        description="Bloques de horario donde el estudiante NO puede asistir"
    )


@router.post(
    "/from-vision",
    response_model=GenerateScheduleResponse,
    summary="Genera horarios a partir de datos de Vision",
    description="""
    Flujo completo automático:
    
    1. Recibe JSON del kárdex (materias cursadas/reprobadas)
    2. Recibe JSON de la oferta académica (materias disponibles)
    3. Cruza información para encontrar materias elegibles
    4. Genera y rankea horarios optimizados
    
    Ideal para conectar directamente con la salida del Vision API.
    """
)
async def generate_from_vision(
    request: VisionToScheduleRequest
) -> GenerateScheduleResponse:
    """Genera horarios a partir de datos extraídos por Vision."""
    
    try:
        logger.info("Procesando flujo Vision → Schedule")
        
        # 1. Extraer materias aprobadas y reprobadas del kárdex
        materias_aprobadas = set()
        materias_reprobadas = set()
        
        semestres = request.kardex_data.get("semestres", [])
        for semestre in semestres:
            for materia in semestre.get("materias", []):
                clave = materia.get("clave", "").upper()
                calificacion = materia.get("calificacion")
                
                if calificacion is not None:
                    if calificacion >= 70:
                        materias_aprobadas.add(clave)
                    else:
                        materias_reprobadas.add(clave)
        
        logger.info(f"Kárdex: {len(materias_aprobadas)} aprobadas, {len(materias_reprobadas)} reprobadas")
        
        # 2. Extraer prerrequisitos del mapa curricular (si se proporciona)
        prerrequisitos_por_clave: Dict[str, List[str]] = {}
        materias_en_mapa: set = set()
        
        if request.mapa_data:
            semestres_mapa = request.mapa_data.get("semestres", [])
            for semestre in semestres_mapa:
                for materia in semestre.get("materias", []):
                    clave_mat = materia.get("clave", "").upper()
                    if clave_mat:
                        materias_en_mapa.add(clave_mat)
                        prereqs = materia.get("prerrequisitos", [])
                        if prereqs:
                            # Normalizar claves de prerrequisitos
                            prerrequisitos_por_clave[clave_mat] = [
                                p.upper() for p in prereqs if p
                            ]
            
            logger.info(f"Mapa curricular: {len(materias_en_mapa)} materias, {len(prerrequisitos_por_clave)} con prerrequisitos")
        
        # 3. Procesar oferta académica
        materias_oferta = request.oferta_data.get("materias", [])
        
        # Agrupar por clave de materia
        materias_por_clave: Dict[str, List[Dict]] = {}
        for mat in materias_oferta:
            clave = mat.get("clave", mat.get("nrc", "")).upper()
            if clave not in materias_por_clave:
                materias_por_clave[clave] = []
            materias_por_clave[clave].append(mat)
        
        logger.info(f"Oferta: {len(materias_por_clave)} materias únicas, {len(materias_oferta)} secciones")
        
        # 4. Filtrar materias elegibles
        # Criterios:
        # - No aprobada (o reprobada para recursar)
        # - Prerrequisitos cumplidos (si hay mapa curricular)
        materias_elegibles = []
        materias_sin_prereqs = []  # Para reportar
        
        for clave, secciones in materias_por_clave.items():
            # Si ya la aprobó, saltar (a menos que sea reprobada también - recurso)
            if clave in materias_aprobadas and clave not in materias_reprobadas:
                continue
            
            # Verificar prerrequisitos (solo si tenemos mapa curricular)
            prereqs = prerrequisitos_por_clave.get(clave, [])
            prereqs_cumplidos = True
            prereqs_faltantes = []
            
            if prereqs:
                for prereq in prereqs:
                    if prereq not in materias_aprobadas:
                        prereqs_cumplidos = False
                        prereqs_faltantes.append(prereq)
            
            if not prereqs_cumplidos:
                primera_seccion = secciones[0]
                nombre = primera_seccion.get("nombre", primera_seccion.get("materia", clave))
                materias_sin_prereqs.append({
                    "clave": clave,
                    "nombre": nombre,
                    "faltantes": prereqs_faltantes
                })
                logger.debug(f"Materia {clave} excluida: faltan prerrequisitos {prereqs_faltantes}")
                continue
            
            # Construir opciones (secciones)
            opciones = []
            primera_seccion = secciones[0]
            nombre = primera_seccion.get("nombre", primera_seccion.get("materia", clave))
            creditos = primera_seccion.get("creditos", 6)
            
            for sec in secciones:
                # Construir horarios
                horarios = []
                horarios_raw = sec.get("horarios", sec.get("horario", []))
                
                # Manejar diferentes formatos de horario
                if isinstance(horarios_raw, list):
                    for h in horarios_raw:
                        if isinstance(h, dict):
                            horarios.append(HorarioInput(
                                dia=h.get("dia", "Lunes"),
                                hora_inicio=h.get("hora_inicio", h.get("inicio", "09:00")),
                                hora_fin=h.get("hora_fin", h.get("fin", "11:00")),
                                aula=h.get("aula")
                            ))
                elif isinstance(horarios_raw, dict):
                    horarios.append(HorarioInput(
                        dia=horarios_raw.get("dia", "Lunes"),
                        hora_inicio=horarios_raw.get("hora_inicio", "09:00"),
                        hora_fin=horarios_raw.get("hora_fin", "11:00"),
                        aula=horarios_raw.get("aula")
                    ))
                
                if horarios:  # Solo agregar si tiene horarios válidos
                    opciones.append(SeccionInput(
                        nrc=sec.get("nrc", str(len(opciones))),
                        clave=clave,
                        nombre=nombre,
                        creditos=creditos,
                        profesor=sec.get("profesor"),
                        cupo_disponible=sec.get("cupo_disponible"),
                        horarios=horarios,
                        modalidad=sec.get("modalidad")
                    ))
            
            if opciones:
                materias_elegibles.append(MateriaElegibleInput(
                    clave=clave,
                    nombre=nombre,
                    creditos=creditos,
                    es_reprobada=clave in materias_reprobadas,
                    es_obligatoria=True,
                    opciones=opciones
                ))
        
        logger.info(f"Materias elegibles: {len(materias_elegibles)}")
        if materias_sin_prereqs:
            logger.info(f"Materias excluidas por prerrequisitos: {len(materias_sin_prereqs)}")
        
        if not materias_elegibles:
            # Construir mensaje más informativo
            mensaje = "No se encontraron materias elegibles."
            if materias_sin_prereqs:
                mensaje += f" {len(materias_sin_prereqs)} materias requieren prerrequisitos que no has aprobado."
            else:
                mensaje += " Verifica que los documentos tengan el formato correcto."
            
            return GenerateScheduleResponse(
                success=False,
                horarios=[],
                total_generados=0,
                mensaje=mensaje,
                advertencias=[
                    f"⚠️ {m['nombre']} ({m['clave']}) requiere: {', '.join(m['faltantes'])}"
                    for m in materias_sin_prereqs[:5]  # Mostrar máximo 5
                ] if materias_sin_prereqs else []
            )
        
        # 5. Filtrar opciones que conflictan con horarios bloqueados
        if request.conflictos:
            logger.info(f"Aplicando {len(request.conflictos)} conflictos de horario")
            materias_filtradas = []
            
            for materia in materias_elegibles:
                opciones_validas = []
                
                for opcion in materia.opciones:
                    tiene_conflicto = False
                    
                    for horario in opcion.horarios:
                        for conflicto in request.conflictos:
                            # Verificar si hay traslape
                            if _horarios_conflictan(
                                horario.dia, horario.hora_inicio, horario.hora_fin,
                                conflicto.dia, conflicto.hora_inicio, conflicto.hora_fin
                            ):
                                tiene_conflicto = True
                                logger.debug(f"Conflicto: {opcion.nombre} ({horario.dia} {horario.hora_inicio}) con {conflicto.dia} {conflicto.hora_inicio}")
                                break
                        if tiene_conflicto:
                            break
                    
                    if not tiene_conflicto:
                        opciones_validas.append(opcion)
                
                # Solo mantener materia si tiene al menos una opción válida
                if opciones_validas:
                    materia_filtrada = MateriaElegibleInput(
                        clave=materia.clave,
                        nombre=materia.nombre,
                        creditos=materia.creditos,
                        es_reprobada=materia.es_reprobada,
                        es_obligatoria=materia.es_obligatoria,
                        opciones=opciones_validas
                    )
                    materias_filtradas.append(materia_filtrada)
            
            logger.info(f"Materias después de filtrar conflictos: {len(materias_filtradas)}")
            materias_elegibles = materias_filtradas
        
        # 6. Construir disponibilidad si se proporcionó
        disponibilidad = None
        if request.disponibilidad:
            disponibilidad = {}
            for dia, bloques in request.disponibilidad.items():
                disponibilidad[dia] = [
                    {"hora_inicio": b["hora_inicio"], "hora_fin": b["hora_fin"]}
                    for b in bloques
                ]
        
        # 7. Generar horarios
        schedule_request = GenerateScheduleRequest(
            materias_elegibles=materias_elegibles,
            disponibilidad=disponibilidad,
            creditos_minimos=request.creditos_minimos,
            creditos_maximos=request.creditos_maximos,
            max_materias=request.max_materias,
            priorizar_reprobadas=request.priorizar_reprobadas,
            evitar_huecos=True,
            max_resultados=request.max_resultados
        )
        
        result = await generate_schedule(schedule_request)
        
        # 8. Agregar advertencias sobre materias excluidas por prerrequisitos
        if materias_sin_prereqs:
            advertencias_prereqs = [
                f"📚 {m['nombre']} ({m['clave']}) requiere aprobar: {', '.join(m['faltantes'])}"
                for m in materias_sin_prereqs[:5]  # Máximo 5 advertencias
            ]
            if len(materias_sin_prereqs) > 5:
                advertencias_prereqs.append(f"... y {len(materias_sin_prereqs) - 5} materias más con prerrequisitos faltantes")
            
            result.advertencias = advertencias_prereqs + result.advertencias
        
        return result
        
    except Exception as e:
        logger.exception(f"Error en flujo Vision → Schedule: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error procesando documentos: {str(e)}"
        )
