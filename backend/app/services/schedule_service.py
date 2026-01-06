"""
Servicio para generar y optimizar horarios académicos.

Funcionalidades:
- Detectar conflictos entre materias
- Generar todas las combinaciones válidas
- Filtrar por disponibilidad del estudiante
- Rankear horarios por múltiples criterios
"""
import logging
from itertools import combinations, product
from typing import Dict, List, Optional, Set, Tuple

from app.schemas.schedule import (
    BloqueHorario,
    DisponibilidadEstudiante,
    HorarioGenerado,
    HorarioRankeado,
    MateriaElegible,
    MateriaOferta,
    ScheduleGenerateRequest,
    ScheduleGenerateResponse,
)

logger = logging.getLogger(__name__)


class ScheduleService:
    """Servicio para generar horarios optimizados."""
    
    def __init__(self):
        """Inicializa el servicio."""
        # Pesos para el algoritmo de ranking (ajustables)
        self.peso_reprobadas = 25  # Prioridad a materias reprobadas
        self.peso_desbloquean = 15  # Prioridad a materias que desbloquean otras
        self.peso_sin_huecos = 20  # Penalización por huecos
        self.peso_compacto = 15  # Preferir horarios compactos
        self.peso_creditos = 10  # Cumplir meta de créditos
        self.peso_dias_libres = 15  # Preferir menos días con clase
    
    def hay_conflicto(
        self,
        materia1: MateriaOferta,
        materia2: MateriaOferta
    ) -> bool:
        """Verifica si dos materias tienen conflicto de horario.
        
        Args:
            materia1: Primera materia
            materia2: Segunda materia
            
        Returns:
            True si hay traslape en horarios
        """
        for bloque1 in materia1.horarios:
            for bloque2 in materia2.horarios:
                if bloque1.se_traslapa_con(bloque2):
                    return True
        return False
    
    def hay_conflicto_en_grupo(self, materias: List[MateriaOferta]) -> bool:
        """Verifica si hay algún conflicto en un grupo de materias.
        
        Args:
            materias: Lista de materias a verificar
            
        Returns:
            True si hay al menos un conflicto
        """
        for i, m1 in enumerate(materias):
            for m2 in materias[i + 1:]:
                if self.hay_conflicto(m1, m2):
                    return True
        return False
    
    def cumple_disponibilidad(
        self,
        materias: List[MateriaOferta],
        disponibilidad: Optional[DisponibilidadEstudiante]
    ) -> bool:
        """Verifica si todas las materias caben en la disponibilidad.
        
        Args:
            materias: Lista de materias
            disponibilidad: Disponibilidad del estudiante (None = sin restricción)
            
        Returns:
            True si todas las materias caben
        """
        if disponibilidad is None:
            return True
        
        for materia in materias:
            for bloque in materia.horarios:
                if not disponibilidad.esta_disponible(bloque):
                    return False
        return True
    
    def generar_combinaciones(
        self,
        elegibles: List[MateriaElegible],
        creditos_min: int,
        creditos_max: int,
        max_materias: int
    ) -> List[List[MateriaOferta]]:
        """Genera todas las combinaciones válidas de materias.
        
        Para cada materia elegible, elige una sección (NRC).
        Luego genera combinaciones de materias sin conflictos.
        
        Args:
            elegibles: Materias elegibles con sus secciones
            creditos_min: Créditos mínimos
            creditos_max: Créditos máximos
            max_materias: Número máximo de materias
            
        Returns:
            Lista de combinaciones válidas (sin conflictos)
        """
        if not elegibles:
            return []
        
        # Para cada materia, sus opciones de sección
        # Generamos todas las combinaciones de secciones
        combinaciones_validas: List[List[MateriaOferta]] = []
        
        # Primero, ordenar elegibles por prioridad (reprobadas primero)
        elegibles_ordenadas = sorted(
            elegibles,
            key=lambda x: (not x.es_reprobada, -len(x.opciones)),
        )
        
        # Generar combinaciones de diferentes tamaños
        for num_materias in range(1, min(max_materias + 1, len(elegibles_ordenadas) + 1)):
            # Combinaciones de materias elegibles
            for combo_elegibles in combinations(elegibles_ordenadas, num_materias):
                # Verificar créditos
                creditos_combo = sum(e.creditos for e in combo_elegibles)
                if creditos_combo < creditos_min or creditos_combo > creditos_max:
                    continue
                
                # Para cada combinación de elegibles, probar todas las secciones
                opciones_por_materia = [e.opciones for e in combo_elegibles]
                
                # Limitar producto cartesiano para evitar explosión combinatoria
                # (máximo 1000 combinaciones por grupo de materias)
                total_combinaciones = 1
                for opts in opciones_por_materia:
                    total_combinaciones *= len(opts)
                    if total_combinaciones > 1000:
                        # Tomar solo las primeras opciones de cada materia
                        opciones_por_materia = [opts[:3] for opts in opciones_por_materia]
                        break
                
                for combo_secciones in product(*opciones_por_materia):
                    secciones = list(combo_secciones)
                    
                    # Verificar que no hay conflictos
                    if not self.hay_conflicto_en_grupo(secciones):
                        # Copiar metadata de elegibles a las secciones
                        for i, seccion in enumerate(secciones):
                            seccion.es_reprobada = combo_elegibles[i].es_reprobada
                        
                        combinaciones_validas.append(secciones)
        
        logger.info(f"Generadas {len(combinaciones_validas)} combinaciones válidas")
        return combinaciones_validas
    
    def calcular_score(
        self,
        horario: HorarioGenerado,
        creditos_objetivo: int = 18,
        priorizar_reprobadas: bool = True,
        evitar_huecos: bool = True
    ) -> float:
        """Calcula el score de un horario (0-100).
        
        Args:
            horario: Horario a evaluar
            creditos_objetivo: Meta de créditos (default 18)
            priorizar_reprobadas: Si dar más peso a reprobadas
            evitar_huecos: Si penalizar huecos
            
        Returns:
            Score de 0 a 100
        """
        score = 50.0  # Base
        
        # 1. Materias reprobadas (muy importante)
        if priorizar_reprobadas:
            score += horario.materias_reprobadas_incluidas * self.peso_reprobadas
        
        # 2. Materias que desbloquean otras
        score += min(horario.materias_que_desbloquean * 5, self.peso_desbloquean)
        
        # 3. Penalización por huecos
        if evitar_huecos and horario.huecos_minutos > 0:
            # Penalizar proporcionalmente (max 20 puntos de penalización)
            penalizacion_huecos = min(horario.huecos_minutos / 30, self.peso_sin_huecos)
            score -= penalizacion_huecos
        
        # 4. Horario compacto (menos amplitud)
        if horario.amplitud_horaria > 0:
            # Ideal: 4-6 horas de amplitud por día
            amplitud_promedio = horario.amplitud_horaria / max(horario.dias_con_clase, 1)
            if amplitud_promedio <= 360:  # 6 horas o menos
                score += self.peso_compacto
            elif amplitud_promedio <= 480:  # 8 horas
                score += self.peso_compacto * 0.5
        
        # 5. Cumplir meta de créditos
        diferencia_creditos = abs(horario.total_creditos - creditos_objetivo)
        if diferencia_creditos == 0:
            score += self.peso_creditos
        elif diferencia_creditos <= 2:
            score += self.peso_creditos * 0.7
        elif diferencia_creditos <= 4:
            score += self.peso_creditos * 0.4
        
        # 6. Preferir menos días con clase (días libres)
        if horario.dias_con_clase <= 4:
            score += self.peso_dias_libres
        elif horario.dias_con_clase == 5:
            score += self.peso_dias_libres * 0.5
        
        # Normalizar a 0-100
        return max(0, min(100, score))
    
    def generar_explicacion(self, horario: HorarioGenerado) -> Tuple[str, List[str], List[str]]:
        """Genera explicación, pros y contras de un horario.
        
        Args:
            horario: Horario a explicar
            
        Returns:
            Tupla de (explicación, pros, contras)
        """
        pros = []
        contras = []
        
        # Analizar características
        if horario.materias_reprobadas_incluidas > 0:
            pros.append(f"Incluye {horario.materias_reprobadas_incluidas} materia(s) que necesitas re-cursar (prioridad)")
        
        if horario.materias_que_desbloquean > 0:
            pros.append(f"Desbloquea {horario.materias_que_desbloquean} materia(s) para el siguiente semestre")
        
        if horario.huecos_minutos == 0:
            pros.append("Sin huecos entre clases")
        elif horario.huecos_minutos <= 60:
            pros.append(f"Solo {horario.huecos_minutos} minutos de hueco(s)")
        else:
            contras.append(f"{horario.huecos_minutos} minutos de huecos entre clases")
        
        if horario.dias_con_clase <= 4:
            dias_libres = 6 - horario.dias_con_clase
            pros.append(f"{dias_libres} día(s) libre(s) a la semana")
        elif horario.dias_con_clase == 6:
            contras.append("Clases los 6 días de la semana")
        
        if horario.hora_inicio_mas_temprana and horario.hora_inicio_mas_temprana >= "09:00":
            pros.append(f"Primera clase a las {horario.hora_inicio_mas_temprana} (no muy temprano)")
        elif horario.hora_inicio_mas_temprana and horario.hora_inicio_mas_temprana < "08:00":
            contras.append(f"Clase temprana a las {horario.hora_inicio_mas_temprana}")
        
        if horario.hora_fin_mas_tardia and horario.hora_fin_mas_tardia <= "15:00":
            pros.append(f"Sales a las {horario.hora_fin_mas_tardia} (tarde libre)")
        elif horario.hora_fin_mas_tardia and horario.hora_fin_mas_tardia >= "20:00":
            contras.append(f"Clase hasta las {horario.hora_fin_mas_tardia}")
        
        # Generar explicación
        explicacion_partes = []
        
        if pros:
            explicacion_partes.append("Te recomiendo este horario porque: " + "; ".join(pros[:2]))
        
        if contras:
            explicacion_partes.append("Considera que: " + "; ".join(contras[:2]))
        
        explicacion = " ".join(explicacion_partes) if explicacion_partes else "Horario balanceado sin notas especiales."
        
        return explicacion, pros, contras
    
    def generar_horarios(
        self,
        request: ScheduleGenerateRequest
    ) -> ScheduleGenerateResponse:
        """Genera horarios optimizados según los parámetros.
        
        Args:
            request: Parámetros de generación
            
        Returns:
            Response con horarios rankeados
        """
        advertencias = []
        
        # Validar entrada
        if not request.materias_elegibles:
            return ScheduleGenerateResponse(
                success=False,
                total_generados=0,
                horarios=[],
                mensaje="No hay materias elegibles para generar horarios",
                advertencias=["Sube tu kárdex y oferta académica primero"]
            )
        
        # Filtrar materias sin opciones de sección
        elegibles_con_opciones = [
            e for e in request.materias_elegibles if e.opciones
        ]
        
        if not elegibles_con_opciones:
            return ScheduleGenerateResponse(
                success=False,
                total_generados=0,
                horarios=[],
                mensaje="Las materias elegibles no tienen secciones disponibles en la oferta",
                advertencias=["Verifica que la oferta académica esté actualizada"]
            )
        
        if len(elegibles_con_opciones) < len(request.materias_elegibles):
            sin_opciones = len(request.materias_elegibles) - len(elegibles_con_opciones)
            advertencias.append(f"{sin_opciones} materia(s) elegible(s) no están en la oferta actual")
        
        # Generar combinaciones
        logger.info(f"Generando horarios con {len(elegibles_con_opciones)} materias elegibles...")
        combinaciones = self.generar_combinaciones(
            elegibles=elegibles_con_opciones,
            creditos_min=request.creditos_minimos,
            creditos_max=request.creditos_maximos,
            max_materias=request.max_materias
        )
        
        if not combinaciones:
            return ScheduleGenerateResponse(
                success=False,
                total_generados=0,
                horarios=[],
                mensaje="No se encontraron combinaciones válidas de horarios",
                advertencias=advertencias + [
                    "Intenta con menos materias o un rango de créditos más amplio"
                ]
            )
        
        # Filtrar por disponibilidad
        if request.disponibilidad:
            combinaciones = [
                c for c in combinaciones
                if self.cumple_disponibilidad(c, request.disponibilidad)
            ]
            
            if not combinaciones:
                return ScheduleGenerateResponse(
                    success=False,
                    total_generados=0,
                    horarios=[],
                    mensaje="Ningún horario cabe en tu disponibilidad",
                    advertencias=advertencias + [
                        "Intenta con una disponibilidad más amplia"
                    ]
                )
        
        # Crear objetos HorarioGenerado y calcular métricas
        horarios: List[HorarioGenerado] = []
        for combo in combinaciones:
            horario = HorarioGenerado(materias=combo)
            horario.calcular_metricas()
            horario.score = self.calcular_score(
                horario,
                creditos_objetivo=(request.creditos_minimos + request.creditos_maximos) // 2,
                priorizar_reprobadas=request.priorizar_reprobadas,
                evitar_huecos=request.evitar_huecos
            )
            horarios.append(horario)
        
        # Ordenar por score (mayor = mejor)
        horarios.sort(key=lambda h: h.score, reverse=True)
        
        # Tomar los mejores
        mejores = horarios[:request.max_resultados]
        
        # Generar explicaciones y crear rankeados
        horarios_rankeados: List[HorarioRankeado] = []
        for i, horario in enumerate(mejores):
            explicacion, pros, contras = self.generar_explicacion(horario)
            
            rankeado = HorarioRankeado(
                horario=horario,
                ranking=i + 1,
                explicacion=explicacion,
                pros=pros,
                contras=contras
            )
            horarios_rankeados.append(rankeado)
        
        logger.info(f"Generados {len(horarios_rankeados)} horarios rankeados de {len(combinaciones)} combinaciones")
        
        return ScheduleGenerateResponse(
            success=True,
            total_generados=len(combinaciones),
            horarios=horarios_rankeados,
            mensaje=f"Se encontraron {len(combinaciones)} horarios posibles. Mostrando los {len(horarios_rankeados)} mejores.",
            advertencias=advertencias
        )


# Singleton del servicio
_schedule_service: Optional[ScheduleService] = None


def get_schedule_service() -> ScheduleService:
    """Obtiene la instancia singleton del servicio de horarios.
    
    Returns:
        Instancia de ScheduleService
    """
    global _schedule_service
    if _schedule_service is None:
        _schedule_service = ScheduleService()
    return _schedule_service
