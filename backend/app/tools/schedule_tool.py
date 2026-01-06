"""
LangChain Tool para generar horarios académicos optimizados.

Este tool es compatible con LangGraph y puede ser usado por el agente
para crear combinaciones de horarios basadas en la oferta académica,
el historial del estudiante y su disponibilidad.
"""
import json
import logging
from typing import Any, Dict, List, Optional, Type

from langchain.tools import BaseTool
from pydantic import BaseModel, Field

from app.schemas.schedule import (
    BloqueHorario,
    DisponibilidadEstudiante,
    MateriaElegible,
    MateriaOferta,
    ScheduleGenerateRequest,
)
from app.services.schedule_service import get_schedule_service

logger = logging.getLogger(__name__)


class ScheduleToolInput(BaseModel):
    """Esquema de entrada para el ScheduleTool."""
    
    materias_elegibles: List[Dict[str, Any]] = Field(
        ...,
        description="""Lista de materias que el estudiante puede cursar. Cada materia debe tener:
        - clave: código de la materia (ej: "MAT201")
        - nombre: nombre completo
        - creditos: número de créditos
        - es_reprobada: true si el estudiante la reprobó antes
        - opciones: lista de secciones disponibles, cada una con:
          - nrc: código único de sección
          - clave: código de materia
          - nombre: nombre
          - creditos: créditos
          - profesor: nombre del profesor (opcional)
          - horarios: lista de bloques, cada uno con:
            - dia: "Lunes", "Martes", etc.
            - hora_inicio: "HH:MM" en formato 24hrs
            - hora_fin: "HH:MM"
        """
    )
    
    disponibilidad: Optional[Dict[str, List[Dict[str, str]]]] = Field(
        None,
        description="""Horarios disponibles del estudiante por día. Formato:
        {
          "Lunes": [{"hora_inicio": "09:00", "hora_fin": "15:00"}],
          "Martes": [{"hora_inicio": "09:00", "hora_fin": "18:00"}],
          ...
        }
        Si es null, se asume disponibilidad completa.
        """
    )
    
    creditos_minimos: int = Field(
        default=12,
        description="Mínimo de créditos a cursar (default: 12)"
    )
    
    creditos_maximos: int = Field(
        default=24,
        description="Máximo de créditos a cursar (default: 24)"
    )
    
    max_materias: int = Field(
        default=6,
        description="Número máximo de materias a inscribir (default: 6)"
    )
    
    priorizar_reprobadas: bool = Field(
        default=True,
        description="Si true, prioriza incluir materias que el estudiante reprobó"
    )
    
    max_resultados: int = Field(
        default=3,
        description="Número máximo de horarios a retornar (default: 3)"
    )


class ScheduleTool(BaseTool):
    """Herramienta para generar horarios académicos optimizados.
    
    Toma las materias elegibles del estudiante (basadas en prerrequisitos),
    la oferta académica, y opcionalmente su disponibilidad horaria,
    para generar los mejores horarios posibles.
    
    Examples:
        >>> tool = ScheduleTool()
        >>> result = tool._run(
        ...     materias_elegibles=[
        ...         {
        ...             "clave": "MAT201",
        ...             "nombre": "Cálculo II",
        ...             "creditos": 8,
        ...             "es_reprobada": False,
        ...             "opciones": [
        ...                 {
        ...                     "nrc": "12345",
        ...                     "clave": "MAT201",
        ...                     "nombre": "Cálculo II",
        ...                     "creditos": 8,
        ...                     "horarios": [
        ...                         {"dia": "Lunes", "hora_inicio": "09:00", "hora_fin": "11:00"},
        ...                         {"dia": "Miércoles", "hora_inicio": "09:00", "hora_fin": "11:00"}
        ...                     ]
        ...                 }
        ...             ]
        ...         }
        ...     ]
        ... )
    """
    
    name: str = "schedule_builder"
    description: str = """
    Genera horarios académicos optimizados para el estudiante.
    
    Esta herramienta:
    1. Recibe las materias que el estudiante puede cursar (ya filtradas por prerrequisitos)
    2. Recibe la oferta académica con horarios de cada sección
    3. Opcionalmente recibe la disponibilidad del estudiante
    4. Genera las mejores combinaciones de horarios sin conflictos
    5. Rankea los horarios por: materias reprobadas, menos huecos, días libres
    
    IMPORTANTE: Antes de usar esta herramienta, debes:
    - Analizar el kárdex del estudiante para saber qué materias puede cursar
    - Analizar la oferta académica para tener los horarios de las secciones
    - Opcionalmente, preguntar al estudiante su disponibilidad
    
    Retorna una lista de horarios rankeados con explicaciones.
    """
    args_schema: Type[BaseModel] = ScheduleToolInput
    
    def _parse_materias_elegibles(
        self,
        materias_raw: List[Dict[str, Any]]
    ) -> List[MateriaElegible]:
        """Convierte diccionarios a objetos MateriaElegible."""
        elegibles = []
        
        for m in materias_raw:
            opciones = []
            for opc in m.get("opciones", []):
                # Parsear horarios
                horarios = []
                for h in opc.get("horarios", []):
                    try:
                        bloque = BloqueHorario(
                            dia=h.get("dia", "Lunes"),
                            hora_inicio=h.get("hora_inicio", "09:00"),
                            hora_fin=h.get("hora_fin", "11:00"),
                            aula=h.get("aula")
                        )
                        horarios.append(bloque)
                    except Exception as e:
                        logger.warning(f"Error parseando horario: {e}")
                
                materia_oferta = MateriaOferta(
                    nrc=opc.get("nrc", ""),
                    clave=opc.get("clave", m.get("clave", "")),
                    nombre=opc.get("nombre", m.get("nombre", "")),
                    creditos=opc.get("creditos", m.get("creditos", 6)),
                    profesor=opc.get("profesor"),
                    cupo_disponible=opc.get("disponibles") or opc.get("cupo_disponible"),
                    horarios=horarios,
                    modalidad=opc.get("modalidad")
                )
                opciones.append(materia_oferta)
            
            elegible = MateriaElegible(
                clave=m.get("clave", ""),
                nombre=m.get("nombre", ""),
                creditos=m.get("creditos", 6),
                opciones=opciones,
                es_reprobada=m.get("es_reprobada", False),
                es_obligatoria=m.get("es_obligatoria", True)
            )
            elegibles.append(elegible)
        
        return elegibles
    
    def _parse_disponibilidad(
        self,
        disp_raw: Optional[Dict[str, List[Dict[str, str]]]]
    ) -> Optional[DisponibilidadEstudiante]:
        """Convierte diccionario a DisponibilidadEstudiante."""
        if not disp_raw:
            return None
        
        dias = {}
        for dia, bloques in disp_raw.items():
            bloques_parsed = []
            for b in bloques:
                try:
                    bloque = BloqueHorario(
                        dia=dia,
                        hora_inicio=b.get("hora_inicio", "07:00"),
                        hora_fin=b.get("hora_fin", "22:00")
                    )
                    bloques_parsed.append(bloque)
                except Exception as e:
                    logger.warning(f"Error parseando disponibilidad: {e}")
            
            if bloques_parsed:
                dias[dia] = bloques_parsed
        
        return DisponibilidadEstudiante(dias=dias) if dias else None
    
    def _run(
        self,
        materias_elegibles: List[Dict[str, Any]],
        disponibilidad: Optional[Dict[str, List[Dict[str, str]]]] = None,
        creditos_minimos: int = 12,
        creditos_maximos: int = 24,
        max_materias: int = 6,
        priorizar_reprobadas: bool = True,
        max_resultados: int = 3
    ) -> Dict[str, Any]:
        """Genera horarios optimizados.
        
        Args:
            materias_elegibles: Materias que puede cursar con sus secciones
            disponibilidad: Horarios disponibles del estudiante
            creditos_minimos: Mínimo de créditos
            creditos_maximos: Máximo de créditos
            max_materias: Máximo de materias
            priorizar_reprobadas: Priorizar reprobadas
            max_resultados: Número de horarios a retornar
            
        Returns:
            Diccionario con horarios rankeados y explicaciones
        """
        logger.info(f"ScheduleTool: Generando horarios con {len(materias_elegibles)} materias elegibles")
        
        try:
            # Parsear entrada
            elegibles = self._parse_materias_elegibles(materias_elegibles)
            disp = self._parse_disponibilidad(disponibilidad)
            
            # Crear request
            request = ScheduleGenerateRequest(
                materias_elegibles=elegibles,
                disponibilidad=disp,
                creditos_minimos=creditos_minimos,
                creditos_maximos=creditos_maximos,
                max_materias=max_materias,
                priorizar_reprobadas=priorizar_reprobadas,
                evitar_huecos=True,
                max_resultados=max_resultados
            )
            
            # Generar horarios
            service = get_schedule_service()
            response = service.generar_horarios(request)
            
            # Convertir a diccionario serializable
            result = {
                "success": response.success,
                "total_generados": response.total_generados,
                "mensaje": response.mensaje,
                "advertencias": response.advertencias,
                "horarios": []
            }
            
            for hr in response.horarios:
                horario_dict = {
                    "ranking": hr.ranking,
                    "explicacion": hr.explicacion,
                    "pros": hr.pros,
                    "contras": hr.contras,
                    "score": hr.horario.score,
                    "total_creditos": hr.horario.total_creditos,
                    "total_horas_semana": hr.horario.total_horas_semana,
                    "dias_con_clase": hr.horario.dias_con_clase,
                    "huecos_minutos": hr.horario.huecos_minutos,
                    "hora_inicio": hr.horario.hora_inicio_mas_temprana,
                    "hora_fin": hr.horario.hora_fin_mas_tardia,
                    "materias": []
                }
                
                for mat in hr.horario.materias:
                    mat_dict = {
                        "nrc": mat.nrc,
                        "clave": mat.clave,
                        "nombre": mat.nombre,
                        "creditos": mat.creditos,
                        "profesor": mat.profesor,
                        "es_reprobada": mat.es_reprobada,
                        "horarios": [
                            {
                                "dia": h.dia,
                                "hora_inicio": h.hora_inicio,
                                "hora_fin": h.hora_fin,
                                "aula": h.aula
                            }
                            for h in mat.horarios
                        ]
                    }
                    horario_dict["materias"].append(mat_dict)
                
                result["horarios"].append(horario_dict)
            
            logger.info(f"ScheduleTool: Generados {len(result['horarios'])} horarios")
            return result
            
        except Exception as e:
            logger.exception(f"ScheduleTool error: {e}")
            return {
                "success": False,
                "error": str(e),
                "mensaje": f"Error generando horarios: {e}"
            }
    
    async def _arun(
        self,
        materias_elegibles: List[Dict[str, Any]],
        disponibilidad: Optional[Dict[str, List[Dict[str, str]]]] = None,
        creditos_minimos: int = 12,
        creditos_maximos: int = 24,
        max_materias: int = 6,
        priorizar_reprobadas: bool = True,
        max_resultados: int = 3
    ) -> Dict[str, Any]:
        """Versión async (usa la sync ya que no hay I/O blocking)."""
        return self._run(
            materias_elegibles=materias_elegibles,
            disponibilidad=disponibilidad,
            creditos_minimos=creditos_minimos,
            creditos_maximos=creditos_maximos,
            max_materias=max_materias,
            priorizar_reprobadas=priorizar_reprobadas,
            max_resultados=max_resultados
        )


# Instancia del tool para importar directamente
schedule_tool = ScheduleTool()
