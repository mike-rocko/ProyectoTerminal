"""
Prompts estructurados para Gemini Vision API.
Cada prompt está diseñado para extraer datos específicos en formato JSON.
"""

# ============================================================================
# PROMPT: OFERTA ACADÉMICA
# ============================================================================
OFERTA_ACADEMICA_PROMPT = """
Analiza esta imagen de OFERTA ACADÉMICA universitaria.

Tu tarea es extraer TODA la información visible de las materias/clases ofertadas.

Extrae la información en este formato JSON exacto:
{
  "semestre": "string (ej: 2024-2, Primavera 2024)",
  "universidad": "string o null si no aparece",
  "materias": [
    {
      "nrc": "string (código único de la sección)",
      "clave": "string (código de la materia, ej: MAT201)",
      "nombre": "string (nombre completo de la materia)",
      "seccion": "string o null",
      "creditos": number o null,
      "profesor": "string o null",
      "cupo": number o null,
      "disponibles": number o null,
      "horario": {
        "dias": ["string"] (ej: ["Lunes", "Miércoles", "Viernes"]),
        "hora_inicio": "string (formato 24hrs, ej: 09:00)",
        "hora_fin": "string (formato 24hrs, ej: 10:30)",
        "aula": "string o null"
      },
      "modalidad": "string (Presencial, Virtual, Híbrida) o null"
    }
  ],
  "notas": "string con observaciones importantes o null"
}

REGLAS CRÍTICAS:
1. Extrae TODOS los datos visibles, no omitas ninguna materia
2. Si un campo no es visible, usa null (no inventes datos)
3. Los horarios deben estar en formato 24 horas (14:00, no 2:00 PM)
4. Los días deben estar en español completo (Lunes, no L o Lu)
5. NRC y clave son campos diferentes - NRC es el código de sección
6. Si hay múltiples horarios para una materia, crea entradas separadas
7. Mantén los nombres exactamente como aparecen (mayúsculas/minúsculas)

Responde ÚNICAMENTE con el JSON, sin markdown ni explicaciones adicionales.
"""

# ============================================================================
# PROMPT: MAPA CURRICULAR / PLAN DE ESTUDIOS
# ============================================================================
MAPA_CURRICULAR_PROMPT = """
Analiza esta imagen de MAPA CURRICULAR / PLAN DE ESTUDIOS universitario.

Tu tarea es extraer la estructura completa del plan de estudios, incluyendo
las materias organizadas por semestre y sus prerrequisitos.

Extrae la información en este formato JSON exacto:
{
  "carrera": "string (nombre de la carrera)",
  "plan": "string (código del plan, ej: 2020, 2023-A) o null",
  "total_creditos": number o null,
  "duracion_semestres": number o null,
  "semestres": [
    {
      "numero": number (1, 2, 3...),
      "materias": [
        {
          "clave": "string (código de la materia)",
          "nombre": "string (nombre completo)",
          "creditos": number o null,
          "horas_teoria": number o null,
          "horas_practica": number o null,
          "tipo": "string (Obligatoria, Optativa, Electiva) o null",
          "prerrequisitos": ["string"] (claves de materias previas requeridas),
          "correquisitos": ["string"] (materias que deben cursarse simultáneamente) 
        }
      ]
    }
  ],
  "areas_formacion": [
    {
      "nombre": "string (ej: Formación Básica, Especialidad)",
      "creditos": number o null,
      "color": "string (si hay código de colores) o null"
    }
  ],
  "notas": "string con observaciones importantes o null"
}

REGLAS CRÍTICAS:
1. Identifica TODOS los semestres y materias visibles
2. Los prerrequisitos son las materias que SE DEBEN CURSAR ANTES
3. Si hay flechas o líneas conectando materias, esas son relaciones de prerrequisito
4. Si una materia no tiene prerrequisitos, usa array vacío []
5. Mantén las claves exactamente como aparecen
6. Si hay áreas de formación diferenciadas por color, inclúyelas
7. Algunos mapas usan "Seriación" en lugar de "Prerrequisito" - es lo mismo

Responde ÚNICAMENTE con el JSON, sin markdown ni explicaciones adicionales.
"""

# ============================================================================
# PROMPT: KÁRDEX / HISTORIAL ACADÉMICO
# ============================================================================
KARDEX_PROMPT = """
Analiza esta imagen de KÁRDEX / HISTORIAL ACADÉMICO de un estudiante universitario.

Tu tarea es extraer el historial completo de materias cursadas con sus calificaciones.

Extrae la información en este formato JSON exacto:
{
  "estudiante": {
    "nombre": "string o null",
    "matricula": "string o null",
    "carrera": "string o null",
    "plan": "string o null",
    "semestre_actual": number o null,
    "promedio_general": number o null
  },
  "periodos": [
    {
      "periodo": "string (ej: 2023-1, Otoño 2023)",
      "materias": [
        {
          "clave": "string (código de la materia)",
          "nombre": "string (nombre completo)",
          "creditos": number o null,
          "calificacion": number (0-100) o null,
          "calificacion_letra": "string (A, B, C, NA, NP) o null",
          "estado": "string (Aprobada, Reprobada, En curso, Baja)"
        }
      ],
      "creditos_periodo": number o null,
      "promedio_periodo": number o null
    }
  ],
  "resumen": {
    "creditos_aprobados": number o null,
    "creditos_reprobados": number o null,
    "creditos_totales_plan": number o null,
    "porcentaje_avance": number o null,
    "materias_reprobadas": ["string"] (lista de claves de materias reprobadas)
  },
  "notas": "string con observaciones importantes o null"
}

REGLAS CRÍTICAS:
1. Extrae TODAS las materias de TODOS los periodos visibles
2. Calificaciones menores a 60 o 70 (según universidad) = Reprobada
3. NA = No Acreditada, NP = No Presentó (ambas son reprobatorias)
4. Si ves "Baja" o "Cancelada", el estado es "Baja"
5. Incluye materias en curso si aparecen (sin calificación final)
6. El promedio debe calcularse solo con materias aprobadas
7. Las materias reprobadas son CRÍTICAS - identifícalas todas

Responde ÚNICAMENTE con el JSON, sin markdown ni explicaciones adicionales.
"""

# ============================================================================
# MAPA DE PROMPTS POR TIPO DE DOCUMENTO
# ============================================================================
VISION_PROMPTS = {
    "oferta": OFERTA_ACADEMICA_PROMPT,
    "mapa": MAPA_CURRICULAR_PROMPT,
    "kardex": KARDEX_PROMPT
}

def get_prompt(doc_type: str) -> str:
    """Obtiene el prompt correspondiente al tipo de documento.
    
    Args:
        doc_type: Tipo de documento ("oferta", "mapa", "kardex")
        
    Returns:
        String con el prompt estructurado
        
    Raises:
        ValueError: Si el tipo de documento no es válido
    """
    if doc_type not in VISION_PROMPTS:
        valid_types = list(VISION_PROMPTS.keys())
        raise ValueError(f"Tipo de documento inválido: {doc_type}. Válidos: {valid_types}")
    
    return VISION_PROMPTS[doc_type]
