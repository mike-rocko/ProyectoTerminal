# PROTOCOLO DE PROYECTO TERMINAL
## Sistema Inteligente de Recomendación de Carga Académica

**Universidad del Caribe**  
**Proyecto Terminal 2024-2025**  

**Estudiantes:**
- David Emmanuel Jauregui
- Oscar Ruiz  
- Gustavo Iván Meraz

---

## 1. RESUMEN

Las instituciones de educación superior enfrentan una limitación estructural: la imposibilidad de proveer acompañamiento académico personalizado a cada estudiante debido a la desproporción entre la población estudiantil y la disponibilidad de asesores académicos. Esta problemática sistémica se intensifica en universidades con planes de estudio flexibles, donde la libertad de elección de asignaturas, sin una guía adecuada, puede derivar en errores de inscripción, rezago académico y prolongación del tiempo de titulación.

El presente proyecto propone el diseño e implementación de un **Sistema Inteligente de Recomendación de Carga Académica** basado en una arquitectura híbrida que integra tres componentes: (1) un sistema experto para validación de prerrequisitos y normatividad, (2) un motor de optimización multiobjetivo para generación de cargas académicas óptimas, y (3) un agente conversacional basado en modelos de lenguaje para interacción en lenguaje natural.

El sistema aborda específicamente el proceso de recomendación de carga académica como un problema de optimización con restricciones, generando múltiples opciones justificadas que consideran tanto las reglas institucionales como las condiciones particulares del estudiante (disponibilidad horaria, recuperación de materias, avance curricular).

Los beneficios esperados incluyen: reducción de errores de inscripción, optimización del avance académico, democratización del acceso a asesoría de calidad las 24 horas, y generación de datos para la mejora continua de los procesos de tutoría institucional.

---

## 2. ANTECEDENTES

### 2.1. Contexto: La Crisis de Escalabilidad en Tutoría Académica

La tutoría académica personalizada ha sido históricamente reconocida como un factor determinante en el éxito estudiantil (Tinto, 1993). Sin embargo, el modelo tradicional de tutoría humana individual presenta limitaciones estructurales de escalabilidad. De acuerdo con Rodríguez-Gómez et al. (2020), en América Latina, la proporción promedio es de 1 tutor por cada 50-80 estudiantes, lo que hace imposible una atención verdaderamente personalizada.

Esta problemática se agrava en contextos de planes de estudio flexibles, donde la autonomía del estudiante para construir su trayectoria académica requiere, paradójicamente, mayor acompañamiento especializado. La complejidad aumenta al considerar factores como prerrequisitos, seriación, disponibilidad de grupos, conflictos de horario y reglamentación institucional.

### 2.2. Inteligencia Artificial en Educación Superior

Los avances recientes en inteligencia artificial han posibilitado la integración de sistemas automatizados de acompañamiento estudiantil. Olaya Mieles et al. (2025) documentan que el uso de chatbots y asistentes inteligentes en contextos educativos ha demostrado mejoras significativas en accesibilidad y tiempos de respuesta, aunque su eficacia pedagógica depende críticamente de la arquitectura del sistema.

#### Sistemas Expertos en Tutoría

Moreno et al. (2012) desarrollaron un modelo de agente inteligente para servicios de apoyo estudiantil, destacando que los sistemas tradicionales de gestión académica son limitados al no ofrecer interacción dinámica. Su propuesta arquitectónica considera al agente como mediador entre el estudiante y la complejidad administrativa, sentando bases para sistemas reactivos capaces de validar reglas institucionales.

#### Optimización de Trayectorias Académicas

Desde la perspectiva algorítmica, el problema de recomendación de carga académica se ha abordado mediante técnicas de optimización combinatoria. Martínez-Torres et al. (2018) modelaron el problema como un sistema de satisfacción de restricciones (CSP) considerando múltiples objetivos: avance curricular, balance de carga de trabajo y preferencias del estudiante.

#### Modelos de Lenguaje en Interfaces Educativas

Bravo y Orjuela (2023) implementaron en la Universidad EAN un sistema de acompañamiento virtual basado en inteligencia artificial diseñado para mejorar la cobertura de servicios de bienestar universitario. Su sistema permite atención instantánea y multicanal, demostrando que la tecnología conversacional reduce significativamente la brecha temporal entre la aparición de una duda y su resolución.

### 2.3. Precedentes Locales

En el contexto de la Universidad del Caribe se han desarrollado iniciativas orientadas a la digitalización de servicios estudiantiles. Proyectos previos implementaron chatbots especializados en trámites administrativos, optimizando tiempos de respuesta y sentando precedentes en la automatización de asesoría institucional. Sin embargo, ninguno ha abordado específicamente el problema de recomendación de carga académica como un proceso de optimización multiobjetivo con validación experta.

---

## 3. DIAGNÓSTICO DEL PROBLEMA

### 3.1. Problemática General: Limitaciones Estructurales de la Tutoría Humana

Las instituciones de educación superior, independientemente de su ubicación geográfica o matrícula, enfrentan una problemática común: **la imposibilidad de asignar un tutor académico por estudiante**. Esta limitación no es local ni coyuntural, sino estructural y sistémica.

Factores que explican esta situación:

1. **Costo-ineficiencia:** La contratación de personal suficiente para tutoría personalizada 1:1 es económicamente inviable (Cabrera y La Nasa, 2000).

2. **Concentración temporal de demanda:** Los periodos de inscripción generan picos de consulta que saturan los servicios de asesoría, imposibilitando atención oportuna.

3. **Horarios limitados:** La asesoría humana opera en horarios laborales, dejando desatendidas las consultas que surgen durante periodos de estudio independiente.

4. **Heterogeneidad de casos:** Cada estudiante presenta una combinación única de historial académico, disponibilidad horaria y objetivos, lo que dificulta la estandarización de recomendaciones.

### 3.2. Impacto Específico: El Problema de la Recomendación de Carga Académica

Dentro del espectro amplio del acompañamiento estudiantil, la **recomendación de carga académica** representa uno de los momentos más críticos. Este proceso, que idealmente debería ser una decisión informada basada en análisis técnico, frecuentemente se convierte en una elección intuitiva con consecuencias potencialmente graves:

**Errores de inscripción por desconocimiento normativo:**
- Incumplimiento de prerrequisitos
- Violación de seriación de asignaturas
- Sobrecarga de créditos en periodos ordinarios
- Selección de materias no elegibles según reglamento

**Suboptimalidad en la trayectoria académica:**
- Horarios con conflictos que obligan a elegir entre materias necesarias
- Períodos con carga insuficiente que retrasan avance curricular
- No priorización de materias reprobadas que bloquean seriación
- Distribución horaria ineficiente con "huecos" improductivos

**Factores socioeconómicos:**
- Incompatibilidad entre horarios académicos y responsabilidades laborales
- Ausencia de herramientas que permitan optimizar disponibilidad de tiempo
- Decisiones forzadas entre estabilidad económica y avance académico

### 3.3. Impacto Institucional

Las consecuencias de un proceso de recomendación de carga académica deficiente trascienden al estudiante individual:

- **Reducción de índices de eficiencia terminal:** Prolongación innecesaria del tiempo de titulación
- **Incremento de rezago académico:** Acumulación de materias no cursadas por decisiones erróneas
- **Carga administrativa adicional:** Corrección de inscripciones incorrectas y gestión de casos de excepción
- **Impacto financiero:** Costos adicionales para estudiantes y costos operativos para la institución

### 3.4. Caso de Estudio: Universidad del Caribe

La Universidad del Caribe, con su modelo educativo flexible, ejemplifica esta problemática. Con un ingreso aproximado de 1,098 estudiantes de nuevo ingreso en 2025 (incremento del 27% respecto al ciclo anterior), la presión sobre los servicios de asesoría académica se intensifica.

**Datos contextuales:**
- Ratio estimado: 1 asesor académico por cada 60-80 estudiantes
- Periodo crítico de inscripción: 2-3 semanas de alta demanda
- Ausencia de herramientas automatizadas de validación previas a inscripción oficial
- Modelo de plan de estudios flexible con opciones de libre elección

**Identificación de necesidad:**
Ante la imposibilidad de escalar el modelo de tutoría humana de manera proporcional al crecimiento matricular, se identifica la necesidad urgente de una **solución tecnológica que democratice el acceso a asesoría académica de calidad**, proveyendo recomendaciones técnicamente fundamentadas, disponibles 24/7, y adaptadas a cada situación individual.

---

## 4. PROPUESTA DE SOLUCIÓN

### 4.1. Descripción General

Se propone el diseño e implementación de un **Sistema Inteligente de Recomendación de Carga Académica** basado en una arquitectura híbrida que integra tres paradigmas de inteligencia artificial:

1. **Inteligencia Artificial Simbólica (Sistema Experto):** Validación de reglas académicas
2. **Optimización Computacional:** Generación de cargas académicas óptimas multiobjetivo
3. **Inteligencia Artificial Generativa (Modelos de Lenguaje):** Interfaz conversacional y explicaciones en lenguaje natural

Esta integración permite que el sistema **no solo recomiende qué materias cursar, sino que explique las razones de cada recomendación**, fomentando una toma de decisiones informada y pedagógicamente valiosa.

### 4.2. Arquitectura del Sistema

```
┌─────────────────────────────────────────────────────────┐
│                  CAPA 1: ENTRADA                        │
│  • Kárdex del estudiante (historial académico)          │
│  • Oferta académica del semestre                        │
│  • Disponibilidad horaria del estudiante                │
│  • Preferencias (carga deseada, prioridades)            │
└────────────────┬────────────────────────────────────────┘
                 │
┌────────────────▼────────────────────────────────────────┐
│          CAPA 2: VALIDACIÓN (Sistema Experto)           │
│                                                         │
│  Reglas Implementadas:                                 │
│  ✓ Validación de prerrequisitos (grafo de dependencias)│
│  ✓ Verificación de seriación obligatoria               │
│  ✓ Cumplimiento de reglamento (límite de créditos)     │
│  ✓ Elegibilidad de asignaturas según historial         │
│                                                         │
│  Output: Conjunto de materias elegibles                │
└────────────────┬────────────────────────────────────────┘
                 │
┌────────────────▼────────────────────────────────────────┐
│    CAPA 3: OPTIMIZACIÓN (Algoritmo Multiobjetivo)      │
│                                                         │
│  Problema: Optimización combinatoria con restricciones │
│                                                         │
│  Objetivos simultáneos:                                │
│  1. Maximizar recuperación de materias reprobadas      │
│  2. Optimizar avance en mapa curricular                │
│  3. Minimizar conflictos de horario                    │
│  4. Maximizar compactación (reducir huecos)            │
│  5. Respetar disponibilidad del estudiante             │
│                                                         │
│  Algoritmo: Backtracking + Heurísticas de poda         │
│                                                         │
│  Output: Top 3-5 combinaciones rankeadas               │
└────────────────┬────────────────────────────────────────┘
                 │
┌────────────────▼────────────────────────────────────────┐
│  CAPA 4: EXPLICACIÓN (Modelo de Lenguaje)              │
│                                                         │
│  • Generación de justificaciones en lenguaje natural   │
│  • Respuestas a preguntas del estudiante               │
│  • Explicación de reglas académicas                    │
│  • Sugerencias de alternativas                         │
│                                                         │
│  Modelo: Google Gemini 1.5 Flash (gratis)             │
└────────────────┬────────────────────────────────────────┘
                 │
┌────────────────▼────────────────────────────────────────┐
│              CAPA 5: SALIDA                             │
│  • 3-5 opciones de carga académica justificadas        │
│  • Visualización de horarios (calendario)              │
│  • Interfaz conversacional para ajustes                │
└─────────────────────────────────────────────────────────┘
```

### 4.3. Componentes Técnicos

#### 4.3.1. Sistema Experto de Validación

**Función:** Actuar como filtro inteligente que reduce el espacio de búsqueda eliminando combinaciones inválidas.

**Implementación:**
- Grafo de prerrequisitos usando NetworkX
- Motor de reglas académicas (Python puro, sin LLM)
- Validación determinística (0% margen de error)

**Reglas implementadas:**
```python
# Ejemplo simplificado
if materia.prerrequisitos:
    for prereq in materia.prerrequisitos:
        if prereq not in kardex.aprobadas:
            materia.elegible = False
```

#### 4.3.2. Motor de Optimización Multiobjetivo

**Función:** Generar cargas académicas que maximicen múltiples objetivos simultáneamente.

**Formulación del problema:**

```
Variables de decisión:
X_i ∈ {0, 1}  para cada materia i elegible

Restricciones:
1. Σ creditos_i * X_i ≤ carga_maxima
2. No conflictos de horario: ∀ (i,j): X_i * X_j * overlap(h_i, h_j) = 0
3. Disponibilidad: ∀ i: X_i → horario_i ∩ disponibilidad ≠ ∅

Objetivos (maximizar):
f1: Prioridad_reprobadas = Σ X_i * (i ∈ reprobadas) * peso_alto
f2: Avance_curricular = Σ X_i * desbloqueos_futuros_i
f3: Compactación = -Σ huecos_en_horario
f4: Balance_días = -variance(creditos_por_dia)
```

**Algoritmo:** Backtracking con poda heurística + scoring multi-criterio

#### 4.3.3. Agente Conversacional

**Función:** Interfaz en lenguaje natural que explica recomendaciones y ajusta restricciones.

**Implementación:**
- **LangChain** como framework de orquestación entre LLMs y herramientas especializadas (LangTools)
- **LangGraph** para definir flujo de estados del agente conversacional
- **Google Gemini 1.5 Flash** como modelo de lenguaje base
- Herramientas especializadas (Tools) para: extracción de documentos (Vision Tool), generación de horarios (Schedule Tool), y consulta de información (RAG Tool)
- Prompts estructurados para explicaciones consistentes

**Nota arquitectónica:** El sistema no implementa un agente desde cero, sino que utiliza LangChain como capa de abstracción que orquesta las llamadas entre el modelo de lenguaje (Gemini) y las herramientas especializadas desarrolladas. LangGraph coordina el flujo conversacional multi-paso.

**Ejemplo de interacción:**
```
Estudiante: "¿Por qué no puedo tomar Bases de Datos Avanzadas?"

Sistema: "No puedes inscribir Bases de Datos Avanzadas por dos razones:
1. Requiere como prerrequisito Bases de Datos I, que reprobaste en 2024-1
2. Según el reglamento Art. 15, debes aprobar todas las materias de nivel 
   básico antes de cursar materias avanzadas.

Te sugiero:
- Inscribir Bases de Datos I en esta carga (está disponible grupo 401, 
  Lu-Mi 16:00-18:00)
- Una vez aprobada, podrás cursar BD Avanzadas el próximo semestre."
```

### 4.4. Propuesta de Valor

**Vs. Sistemas tradicionales de inscripción:**
| Característica | Sistema Tradicional | Sistema Propuesto |
|----------------|--------------------|--------------------|
| Validación | Solo prerrequisitos básicos | Validación experta completa |
| Optimización | Ninguna | Multiobjetivo con algoritmo |
| Explicaciones | No disponibles | Lenguaje natural (LLM) |
| Disponibilidad | Horario laboral | 24/7 |
| Escalabilidad | Limitada por personal | Ilimitada |
| Personalización | Nula | Adaptada a cada estudiante |

**Vs. Otros sistemas académicos con IA:**
- **Integración híbrida:** No solo LLM (que puede "alucinar"), sino validación algorítmica estricta
- **Optimización matemática:** No recomendaciones aleatorias, sino búsqueda exhaustiva en espacio válido
- **Explicabilidad:** No "caja negra", sino justificaciones paso a paso

### 4.5. Alcance

**Incluye:**
- ✅ Modelado de datos académicos (kárdex, oferta, mapa curricular)
- ✅ Sistema experto con reglas académicas
- ✅ Motor de optimización multiobjetivo
- ✅ Generación de 3-5 opciones rankeadas por estudiante
- ✅ Interfaz conversacional (web)
- ✅ Módulo de explicaciones en lenguaje natural
- ✅ Registro de retroalimentación del usuario

**Excluye:**
- ❌ Automatización del proceso oficial de inscripción
- ❌ Modificación de sistemas institucionales existentes
- ❌ Garantía de disponibilidad de cupos en grupos
- ❌ Sustitución total del tutor académico humano

**Restricciones:**
- Dependencia de calidad y actualización de datos institucionales
- Resultados sujetos a disponibilidad real de grupos
- Sistema propone recomendaciones, decisión final es del estudiante

### 4.6. Justificación

**Relevancia académica:**
- Atiende problemática estructural en educación superior
- Integra tres paradigmas de IA en solución coherente
- Genera conocimiento transferible a otras instituciones

**Impacto esperado:**
- **Estudiantes:** Reducción de errores de inscripción, optimización de trayectoria
- **Institución:** Mejora de índices de eficiencia terminal, reducción de carga administrativa
- **Investigación:** Validación de arquitectura híbrida IA-algoritmos en contexto educativo real

**Viabilidad:**
- Tecnología accesible (Google Gemini gratuito, PostgreSQL open source)
- No requiere cambios en sistemas institucionales existentes
- Desarrollo en 16 semanas con equipo de 3 personas

---

## 5. OBJETIVOS

### 5.1. Objetivo General

**Desarrollar un sistema de recomendación de carga académica basado en arquitectura híbrida de inteligencia artificial que integre validación experta, optimización multiobjetivo e interacción en lenguaje natural, aplicable a instituciones de educación superior con planes de estudio flexibles.**

### 5.2. Objetivos Específicos

1. **Implementar un sistema experto** que valide la elegibilidad de asignaturas respetando prerrequisitos, seriación y reglamento académico mediante representación en grafo de dependencias.

2. **Diseñar e implementar un motor de optimización multiobjetivo** que genere cargas académicas óptimas considerando simultáneamente recuperación de materias, avance curricular, compactación de horarios y disponibilidad del estudiante.

3. **Construir una pipeline de procesamiento** que integre extracción de datos académicos, validación de reglas, optimización de combinaciones y generación de explicaciones en un flujo coherente.

4. **Desarrollar un agente conversacional** impulsado por modelos de lenguaje que traduzca las recomendaciones del sistema a explicaciones comprensibles y permita ajuste de restricciones mediante diálogo natural.

5. **Evaluar la efectividad del sistema** mediante métricas de satisfacción del usuario, precisión de recomendaciones y utilidad percibida en un grupo piloto de estudiantes.

---

## 6. METODOLOGÍA

### 6.1. Tipo de Investigación y Enfoque Metodológico

**Investigación aplicada** con metodología ágil **Extreme Programming (XP)** (Beck & Andres, 2004) ejecutada en 16 semanas con iteraciones de 2 semanas.

**Justificación de Extreme Programming:**
XP es particularmente adecuada para este proyecto debido a:
- **Requisitos evolutivos:** El sistema de recomendación académica requiere retroalimentación continua de usuarios reales para refinar reglas y algoritmos
- **Equipo pequeño:** 3 desarrolladores permiten comunicación directa y pair programming efectivo
- **Entrega incremental:** Cada componente (validador, optimizador, agente) puede entregarse y probarse de forma independiente
- **Integración continua:** La arquitectura modular (herramientas LangChain + algoritmos) facilita testing automatizado
- **No se entrenan modelos:** El proyecto usa APIs pre-entrenadas (Gemini) y algoritmos determinísticos, por lo que no aplican metodologías de machine learning como CRISP-DM

**Prácticas XP adoptadas:**
1. **Planning Game:** Reuniones semanales para priorizar historias de usuario
2. **Pair Programming:** Desarrollo en pares para código crítico (validador, optimizador)
3. **Test-Driven Development (TDD):** Tests unitarios antes de implementación
4. **Continuous Integration:** GitHub Actions para testing automático
5. **Small Releases:** Entregas funcionales cada 2 semanas
6. **Simple Design:** Arquitectura mínima viable, refactorización incremental
7. **Collective Code Ownership:** Todo el equipo puede modificar cualquier parte
8. **Sustainable Pace:** 20 horas/semana por integrante (no crunch)
9. **On-site Customer:** Asesor académico como representante del usuario, feedback semanal

**Recolección de datos mixtos:** Entrevistas con asesores académicos (n=5) para validar reglas de negocio, retrospectivas semanales del equipo, métricas técnicas automatizadas (cobertura de tests, tiempo de respuesta), y evaluación con usuarios finales (n=30).

---

### 6.2. Fases del Proyecto

El proyecto se estructura en **8 iteraciones de 2 semanas** cada una, siguiendo el ciclo XP: Planificación → Desarrollo → Testing → Revisión → Despliegue incremental.

**Iteración 1-2: Fundamentos (Semanas 1-4)** - Análisis + Setup  
*Actividades:* Planning game inicial, entrevistas con asesores académicos, análisis de reglamento académico, configuración de entorno (Docker, CI/CD), historias de usuario prioritarias.  
*Entregables:* Especificación de requisitos, arquitectura base, pipeline CI/CD, modelo de datos inicial.  
*Tests:* Configuración de pytest, primeros tests de infraestructura.  
*Milestone:* Especificación técnica aprobada + CI/CD funcional.

**Iteración 3-4: Sistema Experto (Semanas 5-8)** - Validador de Reglas  
*Actividades:* TDD para motor de reglas, pair programming en lógica compleja, refactorización continua, retrospectivas semanales.  
*Entregables:* Grafo de prerrequisitos (NetworkX), motor de validación académica, API endpoints para validación.  
*Tests:* ≥90% cobertura en módulo de validación, tests con datos académicos reales.  
*Milestone:* Sistema experto con precisión 100% en validación de prerrequisitos.

**Iteración 5-6: Motor de Optimización (Semanas 9-12)** - Schedule Builder  
*Actividades:* Desarrollo en pares del algoritmo de backtracking, experimentación con heurísticas, small releases (versión básica → optimizada), revisión semanal con asesor.  
*Entregables:* Algoritmo de generación de horarios, sistema de scoring multi-criterio, detección de conflictos.  
*Tests:* Tests de rendimiento (<30s), tests con casos reales de estudiantes, validación de lógica combinatoria.  
*Milestone:* Generador produce ≥3 opciones válidas para 90% de casos.

**Iteración 7: Integración LangChain (Semanas 13-14)** - Agente Conversacional  
*Actividades:* Desarrollo incremental del agente, integración continua con componentes previos, validación de prompts, testing de flujos conversacionales.  
*Implementación técnica:*  
- Integración de **LangChain** como orquestador entre Gemini y herramientas especializadas
- Desarrollo de LangTools personalizadas: VisionTool (procesamiento documentos), ScheduleTool (llamada al optimizador), RAGTool (búsqueda semántica)
- **LangGraph** para flujo conversacional con estados (router → tools → response)
- NO se construye un agente desde cero: se aprovecha la arquitectura de LangChain para tool calling  
*Entregables:* Agente conversacional funcional, interfaz web (Streamlit), integración Vision API.  
*Tests:* Tests de integración end-to-end, validación de prompts, simulación de conversaciones.  
*Milestone:* Chat funcional que orquesta las 3 herramientas principales.

**Iteración 8: Validación con Usuarios (Semanas 15-16)** - Prueba Piloto  
*Actividades:* Reclutamiento participantes, ejecución de estudio cuasi-experimental (grupo experimental n=15, control n=15), recopilación de métricas, bug fixing basado en feedback real, refactorización final.  
*Entregables:* Sistema en producción (Cloud Run), reporte de validación con análisis estadístico, documentación técnica y académica.  
*Tests:* Tests de carga, monitoreo de métricas de uso real, análisis de logs.  
*Milestone:* Validación exitosa: SUS ≥70, reducción de errores ≥50%.

---

### 6.3. Diagrama del Proceso Metodológico

*Figura 1*

*Extreme Programming (iterativo) integrado con CRISP-DM (componente IA)*

*Figura 1*

*Ciclo Extreme Programming (iteraciones de 2 semanas)*

```
┌─────────────────────────────────────────────────────────────────┐
│               EXTREME PROGRAMMING (16 SEMANAS)                  │
│                    8 ITERACIONES × 2 SEMANAS                    │
└─────────────────────────────────────────────────────────────────┘

        CICLO DE UNA ITERACIÓN (2 semanas)

┌──────────────────────────────────┐
│  LUNES: PLANNING GAME            │
├──────────────────────────────────┤
│ • Historias de usuario           │
│ • Estimación (planning poker)    │
│ • Priorización por valor         │
│ • Asignación de tareas en pares  │
│ • Commitment del equipo          │
└────────────┬─────────────────────┘
             │
             ▼
┌──────────────────────────────────┐
│  MARTES-JUEVES: DESARROLLO       │
├──────────────────────────────────┤
│ • Standup diario (9:00 AM, 15min)│
│ • Pair programming (rotativo)    │
│ • TDD continuo:                  │
│   1. Escribir test (falla)       │
│   2. Escribir código (pasa)      │
│   3. Refactorizar                │
│ • Continuous Integration:        │
│   - Push a main diario           │
│   - CI/CD automático (tests)     │
│   - Feedback inmediato           │
└────────────┬─────────────────────┘
             │
             ▼
┌──────────────────────────────────┐
│  VIERNES SEMANA 1: INTEGRACIÓN   │
├──────────────────────────────────┤
│ • Merge de features              │
│ • Tests de integración           │
│ • Deploy a staging               │
│ • Code review colectivo          │
└────────────┬─────────────────────┘
             │
             ▼
┌──────────────────────────────────┐
│  VIERNES SEMANA 2: RELEASE       │
├──────────────────────────────────┤
│ • Demo al asesor (30 min)        │
│ • Deploy a producción            │
│ • Retrospectiva (1 hr):          │
│   - ¿Qué salió bien?             │
│   - ¿Qué mejorar?                │
│   - Acciones para próximo sprint │
│ • Celebrar logros                │
└────────────┬─────────────────────┘
             │
             └──► SIGUIENTE ITERACIÓN

COMPONENTES CLAVE:

┌─────────────────────────────────────────────────────────────┐
│  PRÁCTICAS XP APLICADAS EN EL PROYECTO                      │
├─────────────────────────────────────────────────────────────┤
│ ✓ Planning Game: Semanal (priorización historias)          │
│ ✓ Small Releases: Deploy incremental cada 2 semanas        │
│ ✓ Simple Design: Arquitectura mínima, refactorizar después │
│ ✓ Testing: TDD + CI/CD (GitHub Actions)                    │
│ ✓ Pair Programming: Código crítico (validador, optimizador)│
│ ✓ Collective Ownership: Todo el equipo modifica todo       │
│ ✓ Continuous Integration: Merges diarios a main            │
│ ✓ Sustainable Pace: 20 hrs/sem (no burnout)                │
│ ✓ On-site Customer: Asesor académico (feedback semanal)    │
└─────────────────────────────────────────────────────────────┘

ARQUITECTURA TÉCNICA (NO SE CONSTRUYE AGENTE DESDE CERO):

┌─────────────────────────────────────────────────────────────┐
│  ORQUESTACIÓN CON LANGCHAIN                                 │
├─────────────────────────────────────────────────────────────┤
│                                                             │
│  ┌──────────────┐         ┌──────────────┐                │
│  │   Gemini     │◄────────┤  LangChain   │                │
│  │  (LLM Base)  │         │ (Orquestador)│                │
│  └──────────────┘         └──────┬───────┘                │
│                                   │                         │
│                    ┌──────────────┼──────────────┐         │
│                    │              │              │         │
│            ┌───────▼─────┐ ┌─────▼────┐ ┌──────▼─────┐   │
│            │ VisionTool  │ │Schedule  │ │  RAGTool   │   │
│            │(Docs→JSON)  │ │Tool      │ │(Semantic   │   │
│            │             │ │(Horarios)│ │ Search)    │   │
│            └─────────────┘ └──────────┘ └────────────┘   │
│                                                             │
│  LangGraph: Define flujo conversacional con estados        │
│  LangChain: Tool calling automático (no agent custom)      │
└─────────────────────────────────────────────────────────────┘
```

*Nota.* Metodología basada en Extreme Programming (Beck & Andres, 2004) para desarrollo ágil de software. El proyecto no requiere CRISP-DM ya que no se entrenan modelos de machine learning; se utilizan APIs pre-entrenadas (Gemini) y algoritmos determinísticos. La arquitectura aprovecha LangChain como framework de orquestación, sin implementar un agente desde cero.

---

### 6.4. Criterios de Validación

**Técnica:** Precisión 100%, tiempo <30s, cobertura tests >90%.  
**Usuario:** Satisfacción ≥4/5, reducción errores ≥50%, utilidad ≥80%.  
**Académica:** Revisión por pares, conformidad reglamentaria 100%.

---

### 6.5. Referencias Metodológicas

- **Beck, K., & Andres, C.** (2004). *Extreme Programming Explained: Embrace Change* (2nd ed.). Addison-Wesley Professional.

- **Chase, H.** (2022). *LangChain: Building applications with LLMs through composability*. GitHub. https://github.com/langchain-ai/langchain

---

## 7. CRONOGRAMA

```
┌──────────────────────────────────────────────────────────────────────┐
│  ITERACIONES XP (2 semanas cada una)                                 │
│  Semanas:  1   2   3   4   5   6   7   8   9  10  11  12  13  14  15  16 │
├──────────────────────────────────────────────────────────────────────┤
│ ITERACIÓN 1-2: FUNDAMENTOS Y SETUP                                  │
│  ├─ Planning game inicial   [██]                                    │
│  ├─ Entrevistas asesores    [██]                                    │
│  ├─ Arquitectura y CI/CD    [██]                                    │
│  └─ Modelo de datos         [██]                                    │
│                                 ◆ Hito 1: Especificación + CI/CD    │
├──────────────────────────────────────────────────────────────────────┤
│ ITERACIÓN 3-4: SISTEMA EXPERTO (TDD)                                │
│  ├─ Grafo prerrequisitos        [████]                              │
│  ├─ Motor de validación          [████]                             │
│  ├─ API endpoints                 [████]                            │
│  └─ Tests (cobertura ≥90%)         [████]                           │
│                                         ◆ Hito 2: Validador 100%    │
├──────────────────────────────────────────────────────────────────────┤
│ ITERACIÓN 5-6: OPTIMIZADOR (PAIR PROGRAMMING)                       │
│  ├─ Algoritmo backtracking              [████]                      │
│  ├─ Sistema scoring multi-criterio       [████]                     │
│  ├─ Detección conflictos                  [████]                    │
│  └─ Tests de rendimiento (<30s)            [████]                   │
│                                                 ◆ Hito 3: Scheduler │
├──────────────────────────────────────────────────────────────────────┤
│ ITERACIÓN 7: INTEGRACIÓN LANGCHAIN                                  │
│  ├─ VisionTool + ScheduleTool + RAGTool      [████]                 │
│  ├─ LangGraph (flujo conversacional)          [████]                │
│  ├─ Interfaz web (Streamlit)                   [████]               │
│  └─ Tests de integración end-to-end             [████]              │
│                                                      ◆ Hito 4: MVP  │
├──────────────────────────────────────────────────────────────────────┤
│ ITERACIÓN 8: VALIDACIÓN CON USUARIOS                                │
│  ├─ Prueba piloto (n=30)                            [████]          │
│  ├─ Bug fixing basado en feedback                    [████]         │
│  ├─ Análisis de resultados                            [████]        │
│  └─ Documentación técnica y académica                  [████]       │
│                                                            ◆ Defensa│
└──────────────────────────────────────────────────────────────────────┘

PRÁCTICAS XP TRANSVERSALES (TODAS LAS ITERACIONES):
┌──────────────────────────────────────────────────────────────────────┐
│ • Planning Game:           Lunes de cada iteración (2 hrs)          │
│ • Pair Programming:        Martes-Jueves (rotativo)                 │
│ • Standup Diario:          Todos los días (15 min)                  │
│ • Continuous Integration:  Push diario a main (CI/CD automático)    │
│ • Small Release:           Viernes de cada iteración (deploy)       │
│ • Retrospectiva:           Viernes de cada iteración (1 hr)         │
│ • Testing:                 TDD continuo (test → code → refactor)    │
└──────────────────────────────────────────────────────────────────────┘

Hitos principales:
◆ Hito 1 (Semana 4): Arquitectura base + CI/CD + especificación técnica
◆ Hito 2 (Semana 8): Sistema experto validado (100% precisión reglas)
◆ Hito 3 (Semana 12): Motor de optimización funcional (<30s, ≥3 opciones)
◆ Hito 4 (Semana 14): MVP completo con LangChain + LangGraph operativo
◆ Hito 5 (Semana 16): Validación exitosa (SUS ≥70, errores -50%)
◆ Defensa Final (Semana 16): Presentación ante comité evaluador
```

---

## 8. RECURSOS REQUERIDOS

### 8.1. Recursos Humanos

| Rol | Perfil | Dedicación | Costo |
|-----|--------|------------|-------|
| **Estudiantes (3)** | Ing. Software/TI | 20 hrs/sem cada uno | Proyecto académico |
| **Asesor académico** | Doctor en IA/Educación | 2 hrs/sem | Honorarios institucionales |
| **Participantes piloto** | Estudiantes 3er-5to semestre | 2 hrs (prueba única) | Incentivo: reconocimiento |

### 8.2. Recursos Materiales

| Recurso | Especificación | Costo Mensual | Costo Total |
|---------|---------------|---------------|-------------|
| **Computadoras desarrollo** | 3 laptops (ya disponibles) | $0 | $0 |
| **Servidor desarrollo** | Local (Docker Compose) | $0 | $0 |
| **Google Gemini API** | Free tier (15 req/min) | $0 | $0 |
| **PostgreSQL** | Supabase free tier (500MB) | $0 | $0 |
| **Redis** | Upstash free tier | $0 | $0 |
| **Deploy producción** | Google Cloud Run free tier | $0 | $0 |
| **Dominio web (opcional)** | .com/.mx | $12 USD/año | $12 USD |
| **Licencias software** | Todo open source | $0 | $0 |

### 8.3. Presupuesto Estimado

| Rubro | Costo |
|-------|-------|
| Recursos humanos | $0 (proyecto académico) |
| Infraestructura cloud | $0 (free tiers) |
| Dominio web (opcional) | $12 USD |
| Material de oficina | $50 USD |
| Imprevistos (10%) | $6 USD |
| **TOTAL** | **$68 USD (~$1,360 MXN)** |

**Justificación del costo cero:**
- Proyecto diseñado específicamente para operar en free tiers
- Gemini API: 1M tokens/día gratis (suficiente para MVP)
- Cloud Run: 2M requests/mes gratis
- Supabase: 500MB DB gratis (suficiente para 3 carreras)
- Todo el stack es open source

**Escalabilidad:**
Si el sistema se institucionaliza posteriormente, costos estimados:
- Cloud Run: $50-100 USD/mes (1000 estudiantes)
- PostgreSQL: $25 USD/mes (2GB)
- **Total producción:** ~$100 USD/mes

---

## 9. VALIDACIÓN

### 9.1. Criterios de Éxito

El sistema se considerará exitoso si cumple:

**Criterios técnicos:**
1. **Precisión del sistema experto:** 100% (cero errores de validación normativa)
2. **Tasa de generación de soluciones:** ≥90% (9 de cada 10 estudiantes reciben ≥3 opciones)
3. **Tiempo de procesamiento:** ≤30 segundos por consulta
4. **Disponibilidad del sistema:** ≥95% (uptime)

**Criterios de efectividad académica:**
5. **Reducción de errores de inscripción:** ≥50% vs. método tradicional
6. **Mejora en avance curricular:** Incremento promedio de ≥2 créditos por periodo
7. **Recuperación de reprobadas:** ≥70% de estudiantes incluyen al menos 1 reprobada

**Criterios de usabilidad:**
8. **System Usability Scale (SUS):** ≥70 puntos (aceptable)
9. **Utilidad percibida:** Promedio ≥4/5 en escala Likert
10. **Intención de reuso:** ≥80% de usuarios declaran que volverían a usarlo

### 9.2. Diseño Experimental

**Tipo de estudio:** Cuasi-experimental con grupo control no equivalente

**Población:** Estudiantes de 3er a 5to semestre de Ingeniería en Software, Universidad del Caribe

**Muestra:**
- Grupo experimental: n=15 estudiantes
- Grupo control: n=15 estudiantes
- Asignación: Por conveniencia (voluntarios)

**Variables a medir:**

*Independiente:*
- Uso del sistema (experimental) vs. asesoría tradicional (control)

*Dependientes:*

| Variable | Instrumento | Momento |
|----------|-------------|---------|
| Errores de inscripción | Revisión por asesor académico | Post-inscripción |
| Créditos inscritos | Sistema SIAE | Post-inscripción |
| Reprobadas recuperadas | Análisis kárdex | Post-inscripción |
| Tiempo de decisión | Cronómetro | Durante proceso |
| Satisfacción | Encuesta Likert (15 ítems) | Post-uso |
| Usabilidad | SUS (10 ítems) | Post-uso |

### 9.3. Procedimiento Experimental

**Fase 1: Reclutamiento (Semana 13)**
- Invitación vía correo institucional
- Criterios de inclusión:
  - Estudiante activo 3er-5to semestre
  - Sin sanciones académicas
  - Voluntario informado (consentimiento)
- Conformación de grupos (aleatorio entre voluntarios)

**Fase 2: Capacitación (Semana 13)**
- Grupo experimental: Tutorial de 10 min sobre uso del sistema
- Grupo control: Sesión estándar de asesoría curricular

**Fase 3: Intervención (Semana 14)**
- Grupo experimental:
  1. Subir kárdex al sistema
  2. Indicar disponibilidad horaria
  3. Recibir recomendaciones (3-5 opciones)
  4. Interactuar con chatbot para dudas
  5. Seleccionar carga final
  
- Grupo control:
  1. Consultar oferta académica (sitio web)
  2. Armar horario manualmente
  3. Asistir a asesoría (si lo desean)
  4. Seleccionar carga final

**Fase 4: Recolección de datos (Semana 14-15)**
- Aplicación de encuestas post-uso
- Revisión de cargas académicas por asesor ciego (no sabe qué grupo)
- Comparación con datos institucionales

**Fase 5: Análisis (Semana 15)**
- Estadística descriptiva (medias, desviaciones)
- Pruebas de hipótesis:
  - H₁: μ_errores_experimental < μ_errores_control
  - H₂: μ_satisfacción_experimental > μ_satisfacción_control
- Significancia: α = 0.05

### 9.4. Métricas de Evaluación

#### Métricas Cuantitativas

| Métrica | Fórmula | Meta |
|---------|---------|------|
| **Tasa de error** | (Estudiantes con ≥1 error) / Total | <10% |
| **Avance promedio** | Σ créditos inscritos / n | ≥18 créditos |
| **Tiempo de decisión** | Tiempo_final - Tiempo_inicio | ≤30 min |
| **Comprensibilidad** | Σ respuestas_correctas / preguntas | ≥80% |

#### Métricas Cualitativas

**Entrevistas semiestructuradas post-uso (n=5 del grupo experimental):**

Preguntas guía:
1. ¿Qué te pareció más útil del sistema?
2. ¿Hubo algo confuso o que no entendieras?
3. ¿Confiaste en las recomendaciones? ¿Por qué sí/no?
4. ¿Cambiarías algo del sistema?
5. ¿Lo recomendarías a otros estudiantes?

**Análisis:** Codificación temática de respuestas

### 9.5. Consideraciones Éticas

- **Consentimiento informado:** Documento firmado explicando participación voluntaria
- **Confidencialidad:** Datos anonimizados, sin nombres en reportes
- **No perjuicio:** Grupo control recibe asesoría estándar (no se les quita nada)
- **Derecho a retirarse:** Participantes pueden abandonar en cualquier momento
- **Beneficio post-estudio:** Sistema disponible para todos tras validación

### 9.6. Limitaciones del Estudio

**Reconocidas:**
1. Muestra pequeña (n=30) por ser estudio piloto
2. Sesgo de selección (voluntarios, posiblemente más motivados)
3. Efecto Hawthorne (saber que son observados puede cambiar comportamiento)
4. Generalización limitada (una universidad, una carrera)

**Mitigaciones:**
- Usar estadística no paramétrica si distribuciones no son normales
- Triangular con datos cualitativos de entrevistas
- Documentar limitaciones en conclusiones

---

## 10. REFERENCIAS

Beck, K. y Andres, C. (2004). *Extreme Programming Explained: Embrace Change* (2nd ed.). Addison-Wesley Professional.

Bravo Benavides, V. A. y Orjuela Parra, M. A. (2023). *Desarrollo de un sistema de acompañamiento virtual con Inteligencia Artificial para la mejora de los servicios de bienestar en la universidad EAN* [Proyecto integrador]. Universidad EAN, Bogotá D.C., Colombia.

Cabrera, A. F. y La Nasa, S. M. (2000). Understanding the college-choice process. *New Directions for Institutional Research*, 2000(107), 5-22.

Chase, H. (2022). *LangChain: Building applications with LLMs through composability*. GitHub. https://github.com/langchain-ai/langchain

Martínez-Torres, M. R., Toral, S. L., Barrero, F. y Gallardo, S. (2018). An evolutionary algorithm for course scheduling using a constraint satisfaction model. In *Proceedings of the 10th annual conference on Genetic and evolutionary computation* (pp. 419-426).

Moreno, P. A., Sandoval Valero, E. M. y Rojas López, C. A. (2012). Diseño de un modelo de agente inteligente para el servicio de apoyo a estudiantes en ambientes virtuales de aprendizaje. *Actas de la VI Conferencia ACORN-REDECOM*, Valparaíso, Chile.

Olaya Mieles, B. A., Rodriguez Estrella, D. A. y Consuegra, D. (2025). Chatbots y asistentes inteligentes en el acompañamiento académico: evaluación de su eficacia pedagógica. *Educational Regent Multidisciplinary Journal*, 2(4), 1-13. https://doi.org/10.63969/ns640j75

Rodríguez-Gómez, D., Meneses, J., Gairín, J. y Feixas, M. (2020). They have gone, and now what? Understanding re-enrolment patterns in the Catalan public university system. *Higher Education Research & Development*, 39(4), 696-712.

Tinto, V. (1993). *Leaving college: Rethinking the causes and cures of student attrition* (2nd ed.). University of Chicago Press.

Universidad del Caribe. (2025). *Informe de matrícula estudiantil, ciclo 2024-2025*. Dirección de Servicios Escolares, Cancún, Quintana Roo.

---

## 11. ANEXOS

### Anexo A: Encuesta de Satisfacción (System Usability Scale)

**Instrucciones:** Para cada afirmación, indica tu grado de acuerdo en escala 1-5:
1 = Totalmente en desacuerdo | 5 = Totalmente de acuerdo

1. Creo que me gustaría usar este sistema frecuentemente
2. Encontré el sistema innecesariamente complejo
3. Pensé que el sistema era fácil de usar
4. Creo que necesitaría ayuda técnica para usar este sistema
5. Las diferentes funciones del sistema estaban bien integradas
6. Había demasiada inconsistencia en el sistema
7. Imagino que la mayoría de la gente aprendería a usar este sistema rápidamente
8. Encontré el sistema muy incómodo de usar
9. Me sentí muy seguro/a usando el sistema
10. Necesité aprender muchas cosas antes de poder empezar con este sistema

### Anexo B: Ejemplo de Reglas Académicas Formalizadas

```python
# Regla 1: Prerrequisitos
REGLA_PRERREQUISITOS = {
    "nombre": "Validación de prerrequisitos",
    "descripcion": "Una materia solo puede cursarse si todas sus prerrequisitos están aprobados",
    "fuente": "Reglamento Académico Art. 12",
    "implementacion": """
        if materia.prerrequisitos:
            for prereq in materia.prerrequisitos:
                if prereq.id not in kardex.materias_aprobadas:
                    return False, f"Falta prerrequisito: {prereq.nombre}"
        return True, "Prerrequisitos cumplidos"
    """
}

# Regla 2: Carga máxima
REGLA_CARGA_MAXIMA = {
    "nombre": "Límite de créditos por semestre",
    "descripcion": "En periodo ordinario, máximo 24 créditos. Con promedio >9.0, máximo 30.",
    "fuente": "Reglamento Académico Art. 15",
    "implementacion": """
        limite = 30 if estudiante.promedio >= 9.0 else 24
        if sum(m.creditos for m in materias_seleccionadas) > limite:
            return False, f"Excede límite de {limite} créditos"
        return True, "Carga permitida"
    """
}

# Regla 3: Seriación
REGLA_SERIACION = {
    "nombre": "Respeto de seriación obligatoria",
    "descripcion": "Materias con seriación explícita deben cursarse en orden",
    "fuente": "Mapa curricular oficial",
    "implementacion": """
        for materia in materias_seleccionadas:
            if materia.seriacion_siguiente:
                if materia.seriacion_siguiente in materias_seleccionadas:
                    return False, f"No puedes cursar {materia.nombre} y {materia.seriacion_siguiente.nombre} simultáneamente"
        return True, "Seriación respetada"
    """
}
```

### Anexo C: Arquitectura Técnica Detallada

*(Referirse a documentos técnicos en directorio `/docs/` del repositorio)*

- `ARQUITECTURA.md` - Diagrama de componentes
- `copilot-instructions.md` - Especificaciones técnicas completas
- `PROJECT_PROGRESS.md` - Estado actual del desarrollo

---

**Documento elaborado:** Enero 2025  
**Versión:** 2.0 (Corregida según observaciones del asesor)  
**Autores:** David Emmanuel Jauregui, Oscar Ruiz, Gustavo Iván Meraz  
**Institución:** Universidad del Caribe, Cancún, Q. Roo, México
