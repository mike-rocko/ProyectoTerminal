# GitHub Copilot Instructions - Tutor IA

## 📋 Descripción del Proyecto

**Nombre:** Sistema de Tutoría Inteligente Multi-Universidad

**Objetivo:** Plataforma SaaS que ayuda a estudiantes universitarios a:
1. Armar su mejor horario académico basado en disponibilidad
2. Seleccionar materias respetando prerrequisitos y mapa curricular
3. Consultar información general de su universidad mediante IA

**Tipo de Sistema:** Multi-tenant (múltiples universidades usan la misma plataforma)

**Equipo:**
- David Emmanuel Jauregui
- Oscar Ruiz
- Gustavo Iván Meraz

**Universidad:** Universidad del Caribe
**Semestre:** Terminal 2024

---

## 🛠️ Stack Tecnológico

### Backend
- **Framework:** FastAPI 0.109.0
- **Python:** 3.11
- **Contenedores:** Docker + Docker Compose
- **Base de datos:** PostgreSQL 15 con pgvector
- **Cache:** Redis 7
- **ORM:** SQLAlchemy 2.0.25
- **Migraciones:** Alembic 1.13.1

### Inteligencia Artificial
- **Framework IA:** LangChain 0.1.0 + LangGraph 0.0.20
- **LLM Principal:** Google Gemini 1.5 Pro (con visión multimodal)
- **Embeddings:** Google Generative AI Embeddings
- **Document Processing:** Google Cloud Document AI
- **Observabilidad IA:** LangSmith 0.0.77

### Almacenamiento
- **Imágenes:** Google Cloud Storage
- **Documentos procesados:** PostgreSQL (JSONB)

### Autenticación
- **Tokens:** JWT (PyJWT 2.8.0)
- **Passwords:** Bcrypt (passlib 1.7.4)

### Frontend (Futuro)
- **Opción 1:** Streamlit (prototipo rápido)
- **Opción 2:** Next.js + Vercel (producción)

---

## 🏗️ Arquitectura del Sistema

### Patrón Multi-Tenant
Cada universidad es un "tenant" separado con sus propios:
- Datos (estudiantes, carreras, información)
- Configuración (logo, colores, subdomain)
- Embeddings RAG (información específica de la universidad)

### 🎯 Filosofía: Arquitectura Híbrida IA + Algoritmos
```
┌─────────────────────────────────────────────────────────┐
│                    PRINCIPIO RECTOR                     │
├─────────────────────────────────────────────────────────┤
│ LLM/IA:     Input flexible + Explicaciones naturales    │
│ Algoritmos: Validación estricta + Optimización confiable│
└─────────────────────────────────────────────────────────┘
```

**Regla de Oro:** 
- ✅ IA para procesamiento de documentos y UX
- ✅ Algoritmos para decisiones críticas (prerrequisitos, conflictos)
- ❌ NUNCA confiar solo en LLM para lógica de negocio

### Componentes Principales
```
┌─────────────────────────────────────────────────────────────┐
│                    FastAPI Backend                          │
│                                                             │
│  ┌──────────────────────────────────────────────────┐      │
│  │              LangGraph Agent (Orquestador)        │      │
│  │                                                   │      │
│  │  CAPA 1: EXTRACCIÓN (IA - Flexible)              │      │
│  │  ┌────────────────────────────────────────┐      │      │
│  │  │ Vision Tools (Gemini 1.5 Pro):         │      │      │
│  │  │ - Analizar Oferta Académica            │      │      │
│  │  │ - Analizar Mapa Curricular             │      │      │
│  │  │ - Analizar Kárdex                      │      │      │
│  │  │ Output: JSON estructurado + Pydantic   │      │      │
│  │  └────────────────────────────────────────┘      │      │
│  │                      ↓                            │      │
│  │  CAPA 2: VALIDACIÓN (Algoritmos - Estricta)      │      │
│  │  ┌────────────────────────────────────────┐      │      │
│  │  │ Validator Engine (Python puro):        │      │      │
│  │  │ ✓ Verificar prerrequisitos (grafo)     │      │      │
│  │  │ ✓ Validar créditos acumulados          │      │      │
│  │  │ ✓ Detectar inconsistencias             │      │      │
│  │  │ ✓ Bloquear datos inválidos             │      │      │
│  │  └────────────────────────────────────────┘      │      │
│  │                      ↓                            │      │
│  │  CAPA 3: OPTIMIZACIÓN (Algoritmos - Confiable)   │      │
│  │  ┌────────────────────────────────────────┐      │      │
│  │  │ Schedule Builder (Algoritmo):          │      │      │
│  │  │                                        │      │      │
│  │  │ 1. Filtrar Materias Elegibles:         │      │      │
│  │  │    - Prerrequisitos cumplidos          │      │      │
│  │  │    - No aprobadas                      │      │      │
│  │  │    - Disponibles en oferta             │      │      │
│  │  │                                        │      │      │
│  │  │ 2. Generar Combinaciones:              │      │      │
│  │  │    - Backtracking + Heurísticas        │      │      │
│  │  │    - Validar conflictos de horario     │      │      │
│  │  │    - Respetar disponibilidad alumno    │      │      │
│  │  │                                        │      │      │
│  │  │ 3. Ranking Multi-Criterio:             │      │      │
│  │  │    - Priorizar reprobadas (peso 3x)    │      │      │
│  │  │    - Minimizar huecos (peso 2x)        │      │      │
│  │  │    - Cumplir preferencias (peso 1x)    │      │      │
│  │  │    - Avance curricular (desbloqueos)   │      │      │
│  │  └────────────────────────────────────────┘      │      │
│  │                      ↓                            │      │
│  │  CAPA 4: EXPLICACIÓN (IA - UX)                   │      │
│  │  ┌────────────────────────────────────────┐      │      │
│  │  │ Chat Explainer (Gemini Flash):         │      │      │
│  │  │ - Traducir decisiones a lenguaje       │      │      │
│  │  │   natural                              │      │      │
│  │  │ - Responder "¿Por qué X materia?"      │      │      │
│  │  │ - Sugerir alternativas                 │      │      │
│  │  └────────────────────────────────────────┘      │      │
│  │                                                   │      │
│  │  CAPA 5: RAG (IA - Consultas)                    │      │
│  │  ┌────────────────────────────────────────┐      │      │
│  │  │ RAG Tool (pgvector + Gemini):          │      │      │
│  │  │ - Info general universidad             │      │      │
│  │  │ - Reglamentos académicos               │      │      │
│  │  │ - FAQs                                 │      │      │
│  │  │ Filtro: universidad_id (multi-tenant)  │      │      │
│  │  └────────────────────────────────────────┘      │      │
│  └──────────────────────────────────────────────────┘      │
│                                                             │
│  ┌──────────────────────────────────────────────────┐      │
│  │   PostgreSQL Multi-Tenant                        │      │
│  │   - universidades (tenant)                       │      │
│  │   - estudiantes                                  │      │
│  │   - carreras                                     │      │
│  │   - mapas_curriculares (grafos prerrequisitos)   │      │
│  │   - ofertas_academicas                           │      │
│  │   - sesiones_consultoria (historial)             │      │
│  │   - universidad_info (RAG)                       │      │
│  └──────────────────────────────────────────────────┘      │
│                                                             │
│  ┌──────────────────────────────────────────────────┐      │
│  │   Redis Cache                                    │      │
│  │   - Embeddings procesados                        │      │
│  │   - Grafos de prerrequisitos                     │      │
│  │   - Ofertas académicas activas                   │      │
│  └──────────────────────────────────────────────────┘      │
└─────────────────────────────────────────────────────────────┘
```

### 🔒 Garantías de Confiabilidad

**1. Validación en Capas:**
```python
# Checkpoint 1: Extracción (IA)
datos_raw = vision_tool.extract(image)

# Checkpoint 2: Validación (Pydantic)
try:
    datos_validados = KardexSchema(**datos_raw)
except ValidationError:
    return "Error: datos inconsistentes, revisar documento"

# Checkpoint 3: Lógica de Negocio (Algoritmo)
if not validador.cumple_prerrequisitos(materia, kardex):
    return "Error: prerequisitos no cumplidos"

# Checkpoint 4: Restricciones Físicas (Algoritmo)
if tiene_conflicto_horario(horario):
    return "Error: conflicto de tiempo detectado"
```

**2. No Errores Críticos:**
- ✅ Prerrequisitos: Verificados con grafo dirigido (networkx)
- ✅ Conflictos horario: Validación por intervalos de tiempo
- ✅ Créditos: Sumas matemáticas exactas
- ✅ Disponibilidad: Match booleano estricto
- ❌ NUNCA: "El LLM decide si puede tomar la materia"

**3. Fallbacks:**
```python
if llm_extraction_fails:
    # Opción 1: Pedir al usuario corregir imagen
    # Opción 2: Formulario manual
    # Opción 3: Parsear con regexes si es PDF estructurado
    
# NUNCA: "Asumir datos" o "Dejar pasar errores"
```

---

## 📁 Estructura del Proyecto
```
ProyectoTerminal/
├── backend/
│   ├── app/
│   │   ├── agents/              # Agentes LangGraph
│   │   │   ├── tutor_agent.py   # Agente principal (orquestador)
│   │   │   ├── extractor_agent.py  # Sub-agente: extracción documentos
│   │   │   └── explainer_agent.py  # Sub-agente: explicaciones NL
│   │   │
│   │   ├── tools/               # LangChain Tools (solo I/O con LLM)
│   │   │   ├── vision_tool.py   # Gemini Vision: extraer datos
│   │   │   └── rag_tool.py      # Búsqueda semántica info universidad
│   │   │
│   │   ├── core/                # ALGORITMOS (lógica crítica)
│   │   │   ├── validators.py    # Validadores estrictos
│   │   │   │   ├─ validar_prerrequisitos()
│   │   │   │   ├─ validar_creditos()
│   │   │   │   └─ validar_seriacion()
│   │   │   ├── prerequisite_graph.py  # Grafo de prerrequisitos
│   │   │   ├── schedule_builder.py    # Algoritmo de horarios
│   │   │   │   ├─ filtrar_materias_elegibles()
│   │   │   │   ├─ generar_combinaciones()
│   │   │   │   ├─ detectar_conflictos()
│   │   │   │   └─ rankear_horarios()
│   │   │   └── constraints.py   # Reglas de negocio
│   │   │
│   │   ├── api/                 # Endpoints FastAPI
│   │   │   ├── auth.py          # Login, registro
│   │   │   ├── estudiantes.py   # CRUD estudiantes
│   │   │   ├── consultoria.py   # Endpoint principal del agente
│   │   │   └── universidades.py # Panel admin universidades
│   │   │       ├─ POST /universidades
│   │   │       ├─ POST /universidades/{id}/carreras
│   │   │       ├─ POST /universidades/{id}/info
│   │   │       └─ GET /universidades/{id}/dashboard
│   │   │
│   │   ├── db/                  # Database
│   │   │   ├── session.py       # SQLAlchemy session
│   │   │   └── base.py          # Base declarativa
│   │   │
│   │   ├── models/              # Modelos SQLAlchemy
│   │   │   ├── universidad.py
│   │   │   ├── estudiante.py
│   │   │   ├── carrera.py
│   │   │   ├── mapa_curricular.py   # Estructura + grafo prerrequisitos
│   │   │   ├── oferta_academica.py  # Grupos disponibles
│   │   │   ├── sesion.py
│   │   │   └── universidad_info.py  # Docs para RAG
│   │   │
│   │   ├── schemas/             # Pydantic schemas (validación estricta)
│   │   │   ├── auth.py
│   │   │   ├── estudiante.py
│   │   │   ├── consultoria.py
│   │   │   ├── kardex.py        # Validación de historial
│   │   │   ├── mapa_curricular.py
│   │   │   ├── oferta_academica.py
│   │   │   └── horario.py       # Validación de horarios generados
│   │   │
│   │   ├── services/            # Lógica de negocio (capa intermedia)
│   │   │   ├── auth_service.py
│   │   │   ├── vision_service.py     # Wrapper de vision tool
│   │   │   ├── schedule_service.py   # Wrapper de schedule builder
│   │   │   ├── validator_service.py  # Orquesta validaciones
│   │   │   └── university_service.py # CRUD universidades
│   │   │
│   │   ├── config/              # Configuración
│   │   │   ├── settings.py      # Settings con Pydantic
│   │   │   ├── security.py      # JWT, hashing
│   │   │   └── dependencies.py  # Dependency injection
│   │   │
│   │   ├── __init__.py
│   │   └── main.py              # App FastAPI
│   │
│   ├── alembic/                 # Migraciones de DB
│   │   └── versions/
│   ├── tests/                   # Tests unitarios/integración
│   │   ├── test_validators.py   # CRÍTICO: Tests de validación
│   │   ├── test_schedule_builder.py  # CRÍTICO: Tests algoritmo
│   │   ├── test_constraints.py
│   │   └── test_integration.py
│   ├── Dockerfile
│   ├── requirements.txt
│   ├── .env                     # Variables de entorno (NO en Git)
│   └── alembic.ini
│
├── frontend/                    # Frontend (futuro)
├── docs/                        # Documentación
│   ├── arquitectura.md          # Diagrama de arquitectura
│   ├── algoritmos.md            # Documentación de algoritmos
│   └── validadores.md           # Reglas de validación
├── uploads/                     # Imágenes temporales
├── .github/
│   ├── workflows/               # CI/CD
│   └── copilot-instructions.md  # Este archivo
├── docker-compose.yml
├── .gitignore
└── README.md
```

### 🎯 Separación Clara de Responsabilidades

**LLM (tools/):** Input/Output flexible
- ✅ Extraer datos de imágenes/PDFs
- ✅ Responder preguntas en lenguaje natural
- ✅ Explicar decisiones del sistema
- ❌ NO tomar decisiones críticas

**Algoritmos (core/):** Lógica confiable
- ✅ Validar prerrequisitos (grafo)
- ✅ Generar combinaciones de horarios
- ✅ Detectar conflictos
- ✅ Rankear opciones
- ✅ Aplicar reglas de negocio

**Servicios (services/):** Orquestación
- Combinar LLM + Algoritmos
- Manejo de errores
- Logging y observabilidad

---

## 🎯 Convenciones de Código

### Naming Conventions

**Python:**
- Variables/funciones: `snake_case`
- Clases: `PascalCase`
- Constantes: `UPPER_SNAKE_CASE`
- Private methods: `_prefijo_underscore`
- Archivos: `snake_case.py`

**Base de datos:**
- Tablas: `snake_case` plural (universidades, estudiantes)
- Columnas: `snake_case`
- Foreign keys: `tabla_id` (ej: universidad_id)
- Timestamps: siempre `created_at`, `updated_at`

**API Endpoints:**
- RESTful: `/api/v1/recurso`
- Plural para colecciones: `/estudiantes`
- Verbos HTTP correctos: GET, POST, PUT, DELETE

### Imports Order
```python
# 1. Standard library
import os
from typing import Optional, List

# 2. Third-party
from fastapi import FastAPI, Depends
from sqlalchemy import Column, String
from pydantic import BaseModel

# 3. Local
from app.core.config import settings
from app.models.estudiante import Estudiante
from app.schemas.auth import Token
```

### Type Hints
**SIEMPRE usar type hints:**
```python
def procesar_imagen(
    image_path: str, 
    doc_type: Literal["oferta", "mapa", "kardex"]
) -> dict:
    ...
```

### Docstrings
**Usar Google style:**
```python
def filtrar_materias_elegibles(
    kardex_data: dict,
    mapa_curricular: dict
) -> List[dict]:
    """Filtra materias que el estudiante puede cursar.
    
    Args:
        kardex_data: Historial académico del estudiante
        mapa_curricular: Plan de estudios de la carrera
        
    Returns:
        Lista de materias elegibles con sus datos
        
    Raises:
        ValueError: Si el kardex está incompleto
    """
    ...
```

---

## 🧠 Patrones y Mejores Prácticas

### 1. Dependency Injection (FastAPI)
```python
# ✅ CORRECTO
from fastapi import Depends
from app.core.dependencies import get_db

@app.get("/estudiantes/{id}")
async def get_estudiante(
    id: str,
    db: Session = Depends(get_db)  # Inyección
):
    ...

# ❌ INCORRECTO
@app.get("/estudiantes/{id}")
async def get_estudiante(id: str):
    db = SessionLocal()  # No hagas esto
    ...
```

### 2. Async/Await (cuando sea posible)
```python
# ✅ Usar async para I/O
async def llamar_gemini(prompt: str) -> str:
    response = await llm.ainvoke(prompt)
    return response

# ⚠️ Sync solo si es necesario (DB sync, etc)
def procesar_imagen_local(path: str) -> bytes:
    with open(path, "rb") as f:
        return f.read()
```

### 3. Manejo de Errores
```python
from fastapi import HTTPException

# ✅ Errores HTTP específicos
if not estudiante:
    raise HTTPException(
        status_code=404,
        detail=f"Estudiante {id} no encontrado"
    )

# ✅ Try/except para external APIs
try:
    response = await gemini.generate(prompt)
except Exception as e:
    logger.error(f"Error en Gemini: {e}")
    raise HTTPException(
        status_code=503,
        detail="Servicio de IA temporalmente no disponible"
    )
```

### 4. Logging
```python
import logging

logger = logging.getLogger(__name__)

# ✅ Log niveles apropiados
logger.debug("Procesando imagen...")
logger.info(f"Estudiante {id} creó sesión")
logger.warning(f"Imagen de baja calidad detectada")
logger.error(f"Error al procesar: {error}")
```

### 5. Environment Variables
```python
# ✅ Usar Pydantic Settings
from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    database_url: str
    google_api_key: str
    
    class Config:
        env_file = ".env"

settings = Settings()
```

### 6. Multi-Tenancy
```python
# ✅ SIEMPRE filtrar por universidad_id
query = db.query(Estudiante).filter(
    Estudiante.universidad_id == universidad_id
)

# ❌ NUNCA queries globales sin filtro
query = db.query(Estudiante).all()  # PELIGRO: mezcla universidades
```

---

## 🤖 Guías Específicas para IA/LangChain

### LangChain Tools
```python
# Estructura base de un Tool
from langchain.tools import BaseTool
from pydantic import BaseModel, Field

class MiToolInput(BaseModel):
    param1: str = Field(description="Descripción clara")
    param2: int = Field(description="Otro parámetro")

class MiTool(BaseTool):
    name = "nombre_herramienta"  # snake_case
    description = """Descripción DETALLADA de qué hace.
    El LLM usa esto para decidir cuándo llamarlo."""
    args_schema = MiToolInput
    
    def _run(self, param1: str, param2: int) -> dict:
        """Lógica sync"""
        ...
    
    async def _arun(self, param1: str, param2: int) -> dict:
        """Lógica async (preferida)"""
        ...
```

### Prompts para Gemini Vision
```python
# ✅ Prompts estructurados con output JSON
prompt = """
Analiza esta imagen de OFERTA ACADÉMICA.

Extrae la información en este formato JSON exacto:
{
  "semestre": "string",
  "materias": [
    {
      "nrc": "string",
      "nombre": "string",
      "creditos": number,
      "horario": {...}
    }
  ]
}

REGLAS CRÍTICAS:
- Extrae TODOS los datos visibles
- Si falta algo, usa null
- Horarios en formato 24hrs
- Nombres exactos como aparecen
- NO inventes datos

Responde SOLO con el JSON, sin markdown ni explicaciones.
"""
```

### RAG con pgvector
```python
# Embeddings y búsqueda semántica
from langchain_google_genai import GoogleGenerativeAIEmbeddings
from langchain_postgres.vectorstores import PGVector

embeddings = GoogleGenerativeAIEmbeddings(
    model="models/embedding-001"
)

vectorstore = PGVector(
    embeddings=embeddings,
    collection_name="universidad_info",
    connection_string=settings.database_url
)

# Búsqueda
results = vectorstore.similarity_search(
    query="¿Cuál es la misión de la universidad?",
    k=3,
    filter={"universidad_id": universidad_id}  # Multi-tenant
)
```

---

## 📊 Modelo de Datos (Referencia)

### Tablas Principales

**universidades**
- id (UUID, PK)
- nombre (str)
- slug (str, unique) - ej: "unicaribe", "unam"
- logo_url (str)
- config (JSONB) - colores, info, etc
- created_at (timestamp)

**estudiantes**
- id (UUID, PK)
- universidad_id (UUID, FK)
- matricula (str)
- email (str)
- password_hash (str)
- carrera_id (UUID, FK)
- created_at (timestamp)

**carreras**
- id (UUID, PK)
- universidad_id (UUID, FK)
- nombre (str)
- clave (str)
- plan_estudios (JSONB) - mapa curricular completo

**sesiones_consultoria**
- id (UUID, PK)
- estudiante_id (UUID, FK)
- tipo (enum: "horario", "materias", "combinado")
- img_oferta_url (str)
- img_mapa_url (str)
- img_kardex_url (str)
- oferta_data (JSONB) - datos extraídos
- mapa_data (JSONB)
- kardex_data (JSONB)
- disponibilidad (JSONB) - {"lunes": ["9-11"], ...}
- recomendacion (JSONB) - horario final
- explicacion (text)
- created_at (timestamp)

**universidad_info** (para RAG - Base de Conocimiento)
- id (UUID, PK)
- universidad_id (UUID, FK)
- tipo (enum) - "general", "reglamento", "materia", "organigrama", "faq", "enlace"
- categoria (str) - "academico", "administrativo", "servicios", etc.
- titulo (str) - Título del documento/info
- contenido (text) - Contenido completo
- url (str, nullable) - Link si aplica
- archivo_url (str, nullable) - GCS path si es PDF/imagen
- metadata (JSONB) - {"keywords": [...], "fecha": "", "autor": ""}
- embedding (vector) - Para búsqueda semántica
- created_at (timestamp)
- updated_at (timestamp)

---

## 🔐 Seguridad

### Autenticación JWT
```python
# Header esperado
Authorization: Bearer <token>

# Payload del token
{
  "sub": "estudiante_id",
  "universidad_id": "uuid",
  "exp": timestamp
}
```

### Validaciones
- ✅ SIEMPRE validar universidad_id matches token
- ✅ Validar tipos de archivo (solo imágenes: jpg, png, pdf)
- ✅ Límite de tamaño de imagen: 10MB
- ✅ Rate limiting en endpoints públicos
- ✅ SQL injection prevention (usar ORM, no raw queries)

---

## 🧪 Testing

### Estructura de Tests
```python
# tests/test_vision_tool.py
import pytest
from app.tools.vision_tool import VisionTool

@pytest.mark.asyncio
async def test_vision_tool_oferta():
    tool = VisionTool()
    result = await tool._arun(
        image_path="tests/fixtures/oferta_ejemplo.jpg",
        doc_type="oferta"
    )
    
    assert "materias" in result
    assert len(result["materias"]) > 0
    assert result["materias"][0]["nrc"] is not None
```

### Fixtures
```python
# tests/conftest.py
import pytest
from sqlalchemy import create_engine
from app.db.base import Base

@pytest.fixture
def db_session():
    engine = create_engine("sqlite:///:memory:")
    Base.metadata.create_all(engine)
    # ... setup
    yield session
    # ... teardown
```

---

## 📝 Git Workflow

### Branch Strategy
- `main` - Producción (protegida)
- `dev` - Desarrollo (integración)
- `feature/nombre` - Features individuales
- `fix/nombre` - Bugfixes

### Commit Messages
```
feat: añadir vision tool para analizar ofertas
fix: corregir filtro de materias elegibles
docs: actualizar README con instrucciones
refactor: mejorar estructura de schedule builder
test: agregar tests para vision tool
chore: actualizar dependencias
```

### Pull Requests
- Título descriptivo
- Descripción de cambios
- Screenshots si es UI
- Link a issue relacionado
- Al menos 1 reviewer

---

## 🚨 Errores Comunes a Evitar

### ❌ NO hacer:
```python
# Queries sin filtro multi-tenant
db.query(Estudiante).all()

# Hardcodear credenciales
api_key = "AIza..."

# Imports relativos incorrectos
from ..models import Estudiante  # NO

# Bloqueantes en async
def async_func():
    time.sleep(5)  # NO en async

# Try/except sin logging
try:
    ...
except:
    pass  # NUNCA hacer esto
```

### ✅ SÍ hacer:
```python
# Filtrar por tenant
db.query(Estudiante).filter(
    Estudiante.universidad_id == uni_id
).all()

# Variables de entorno
api_key = settings.google_api_key

# Imports absolutos
from app.models.estudiante import Estudiante

# Async apropiado
async def async_func():
    await asyncio.sleep(5)

# Logging de errores
try:
    ...
except Exception as e:
    logger.error(f"Error: {e}")
    raise
```

---

## 🎯 Contexto del Negocio

### Problema que Resolvemos
Estudiantes universitarios pierden tiempo armando horarios manualmente y cometen errores:
- Se inscriben a materias sin cumplir prerrequisitos
- Arman horarios con huecos innecesarios
- No optimizan su carga académica
- Carecen de información clara sobre su universidad

### Propuesta de Valor
1. **Para Estudiantes:** 
   - Horarios optimizados en 5 minutos vs 2+ horas manual
   - Consulta información de universidad 24/7 (chatbot IA)
   - Recomendaciones de materias basadas en prerrequisitos
   
2. **Para Universidades:** 
   - Reduce errores de inscripción y rezago académico
   - Centraliza información institucional accesible
   - Dashboard de métricas de uso
   
3. **Diferenciador Técnico:** 
   - Acepta documentos en **cualquier formato** (PDF, imagen, Excel, foto)
   - Cada universidad tiene formatos diferentes → Vision AI flexible
   - Sistema híbrido: IA extrae, Algoritmos validan (0% errores críticos)

### KPIs del Proyecto
- Precisión extracción: >90% en datos de imágenes
- Tiempo respuesta: <30 segundos por consulta
- Satisfacción: >4/5 estrellas de estudiantes
- Universidades piloto: 3 (UniCaribe + 2 más)

---

## 💬 Guías de Comunicación del Código

### Comentarios
```python
# ✅ Buenos comentarios (explican POR QUÉ)
# Usamos timeout de 30s porque Gemini puede tardar en imágenes grandes
response = await llm.ainvoke(prompt, timeout=30)

# Filtrar reprobadas primero para priorizarlas (requisito negocio)
reprobadas = [m for m in materias if m["calificacion"] < 70]

# ❌ Malos comentarios (redundantes)
# Crear variable x
x = 5
```

### TODOs
```python
# TODO(david): Implementar caché de embeddings para reducir llamadas
# FIXME: Este filtro falla con materias sin prerrequisitos
# HACK: Workaround temporal hasta que Gemini soporte PDFs grandes
# NOTE: Este algoritmo es O(n²), optimizar si n > 1000
```

---

## 🔄 CI/CD (Futuro)

### GitHub Actions Workflow
```yaml
# .github/workflows/test.yml
name: Tests
on: [push, pull_request]
jobs:
  test:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
      - name: Run tests
        run: |
          docker-compose run backend pytest
```

---

## 📚 Referencias Útiles

### Documentación Oficial
- FastAPI: https://fastapi.tiangolo.com/
- LangChain: https://python.langchain.com/
- LangGraph: https://langchain-ai.github.io/langgraph/
- Gemini: https://ai.google.dev/docs
- SQLAlchemy: https://docs.sqlalchemy.org/

### Ejemplos de Código Similar
- Multi-tenant FastAPI: https://github.com/tiangolo/fastapi/discussions/3853
- LangChain Vision: https://python.langchain.com/docs/integrations/chat/google_generative_ai

---

## 🎓 Notas Finales

Este es un **proyecto académico terminal** pero se desarrolla con **estándares profesionales**.

**Prioridades:**
1. Funcionalidad core (vision + schedule builder)
2. Código limpio y mantenible
3. Documentación clara
4. Testing básico

**No priorizar (por tiempo):**
- Optimizaciones prematuras
- Casos edge muy raros
- UI perfecta (MVP primero)

**Principio KISS:** Keep It Simple, Stupid
- Si hay 2 formas de hacer algo, elige la más simple
- Código legible > Código "clever"
- MVP funcional > Features perfectas incompletas

---

**Fecha:** Diciembre 2024  
**Deadline:** ~12 semanas  
**Equipo:** 3 estudiantes  
**Alcance:** MVP con 1 universidad piloto (UniCaribe)

---

## 👥 Flujos de Usuario Detallados

### 🏛️ Flujo: Universidad (Admin)
```
┌─────────────────────────────────────────────────────────┐
│ 1. REGISTRO DE UNIVERSIDAD                             │
├─────────────────────────────────────────────────────────┤
│ Input: nombre, email admin, logo                       │
│ Sistema: Crea tenant, genera subdomain, credenciales   │
│ Output: URL personalizada (unicaribe.tutorai.com)      │
└─────────────────────────────────────────────────────────┘
                        ↓
┌─────────────────────────────────────────────────────────┐
│ 2. LOGIN PANEL ADMIN                                    │
├─────────────────────────────────────────────────────────┤
│ URL: admin.tutorai.com/login                           │
│ Auth: JWT con rol "admin_universidad"                  │
└─────────────────────────────────────────────────────────┘
                        ↓
┌─────────────────────────────────────────────────────────┐
│ 3. CONFIGURAR INFORMACIÓN (BASE DE CONOCIMIENTO RAG)  │
├─────────────────────────────────────────────────────────┤
│ Tipos de Contenido Soportados:                        │
│                                                         │
│ A) INFORMACIÓN GENERAL:                               │
│    ├─ Misión y Visión (texto)                        │
│    ├─ Historia de la universidad                    │
│    ├─ Valores institucionales                       │
│    └─ Contactos (teléfonos, emails, direcciones)   │
│                                                         │
│ B) DOCUMENTOS ACADÉMICOS:                            │
│    ├─ Calendario Académico (PDF/imagen/Excel)      │
│    ├─ Reglamentos (PDFs múltiples)                  │
│    ├─ Planes de estudio                            │
│    └─ Políticas de titulación                       │
│                                                         │
│ C) DETALLES DE MATERIAS:                               │
│    ├─ Descripciones detalladas                      │
│    ├─ Seriación y prerrequisitos                   │
│    └─ Bibliografía recomendada                      │
│                                                         │
│ D) ESTRUCTURAS ORGANIZACIONALES:                       │
│    ├─ Organigrama (PDF/imagen)                      │
│    ├─ Directorio de profesores                      │
│    └─ Departamentos y coordinaciones                │
│                                                         │
│ E) ENLACES Y RECURSOS:                                 │
│    ├─ Links a sistemas (SIAE, biblioteca, etc)      │
│    ├─ Recursos digitales                            │
│    └─ Servicios estudiantiles                       │
│                                                         │
│ F) FAQs:                                               │
│    ├─ Preguntas frecuentes administrativas          │
│    ├─ Preguntas académicas                           │
│    └─ Preguntas de servicios                        │
│                                                         │
│ Formatos Aceptados:                                    │
│ • Texto directo (formulario web)                      │
│ • PDF                                                 │
│ • Imagen (JPG, PNG)                                  │
│ • Word/Excel                                          │
│ • URLs (links externos)                              │
│                                                         │
│ Sistema:                                               │
│ 1. Procesa documentos con Vision AI                    │
│ 2. Genera embeddings con Gemini                        │
│ 3. Almacena en pgvector                                │
│ 4. Filtra por universidad_id (multi-tenant)            │
│                                                         │
│ Output: Base de conocimiento lista para RAG            │
└─────────────────────────────────────────────────────────┘
                        ↓
┌─────────────────────────────────────────────────────────┐
│ 4. GESTIONAR CARRERAS                                   │
├─────────────────────────────────────────────────────────┤
│ Crear carrera:                                         │
│ ├─ Nombre: "Ingeniería en Software"                    │
│ ├─ Clave: "ISW"                                        │
│ └─ Subir Mapa Curricular (imagen/PDF)                  │
│                                                         │
│ Sistema: Vision API extrae estructura de prerrequisitos│
│ Output: JSON con materias y relaciones                 │
└─────────────────────────────────────────────────────────┘
                        ↓
┌─────────────────────────────────────────────────────────┐
│ 5. MONITOREO (Dashboard)                                │
├─────────────────────────────────────────────────────────┤
│ Métricas:                                              │
│ ├─ Total estudiantes activos                           │
│ ├─ Consultas este mes                                  │
│ ├─ Satisfacción promedio                               │
│ └─ Documentos procesados                               │
└─────────────────────────────────────────────────────────┘
```

---

### 🎓 Flujo: Estudiante
```
┌─────────────────────────────────────────────────────────┐
│ 1. REGISTRO                                             │
├─────────────────────────────────────────────────────────┤
│ URL: unicaribe.tutorai.com/registro                    │
│ Input:                                                 │
│ ├─ Matrícula                                           │
│ ├─ Email institucional                                 │
│ ├─ Carrera (dropdown)                                  │
│ └─ Contraseña                                          │
│                                                         │
│ Sistema: Valida email @unicaribe.mx, crea cuenta       │
│ Output: Sesión JWT, redirect a dashboard              │
└─────────────────────────────────────────────────────────┘
                        ↓
┌─────────────────────────────────────────────────────────┐
│ 2. DASHBOARD PRINCIPAL                                  │
├─────────────────────────────────────────────────────────┤
│ Opciones:                                              │
│ ┌─────────────────┐  ┌─────────────────┐             │
│ │ 📅 ARMAR        │  │ 📚 QUÉ MATERIAS │             │
│ │    HORARIO      │  │    TOMAR        │             │
│ └─────────────────┘  └─────────────────┘             │
│                                                         │
│ ┌─────────────────┐  ┌─────────────────┐             │
│ │ 🤖 CHAT CON     │  │ 📊 MIS          │             │
│ │    TUTOR IA     │  │    CONSULTAS    │             │
│ └─────────────────┘  └─────────────────┘             │
└─────────────────────────────────────────────────────────┘
                        ↓
┌─────────────────────────────────────────────────────────┐
│ 3A. FLUJO: ARMAR HORARIO                                │
├─────────────────────────────────────────────────────────┤
│ Paso 1: Subir Documentos (drag & drop)                │
│ ┌──────────────────────────────────────────┐          │
│ │ 📄 Oferta Académica (requerido)          │          │
│ │ 📄 Kárdex/Historial (requerido)          │          │
│ │ 📄 Mapa Curricular (opcional si ya existe)│         │
│ └──────────────────────────────────────────┘          │
│                                                         │
│ Validación:                                            │
│ ✓ Formato: JPG, PNG, PDF (< 10MB)                     │
│ ✓ Calidad mínima detectable                           │
└─────────────────────────────────────────────────────────┘
                        ↓
┌─────────────────────────────────────────────────────────┐
│ Paso 2: Especificar Disponibilidad                     │
├─────────────────────────────────────────────────────────┤
│ Interfaz visual (calendario semanal):                  │
│                                                         │
│      L    M    Mi   J    V    S                        │
│ 7   [x]  [x]  [x]  [x]  [x]  [ ]                      │
│ 8   [x]  [x]  [x]  [x]  [x]  [ ]                      │
│ 9   [✓]  [✓]  [✓]  [✓]  [✓]  [ ]  ← Disponible       │
│ 10  [✓]  [ ]  [✓]  [ ]  [✓]  [ ]  x = Bloqueado      │
│ 11  [✓]  [ ]  [✓]  [ ]  [✓]  [ ]  ✓ = Disponible     │
│ ...                                                     │
│                                                         │
│ Opción: "Trabajo de X a Y hrs (bloquear automático)"   │
└─────────────────────────────────────────────────────────┘
                        ↓
┌─────────────────────────────────────────────────────────┐
│ Paso 3: Procesamiento (Loading con Progress)           │
├─────────────────────────────────────────────────────────┤
│ ⏳ Analizando oferta académica...        [████░░] 60%  │
│ ⏳ Extrayendo tu historial académico...  [██████] 100% │
│ ⏳ Verificando prerrequisitos...         [███░░░] 50%  │
│ ⏳ Generando combinaciones de horarios... [░░░░░] 0%   │
│                                                         │
│ Tiempo estimado: 20-30 segundos                        │
└─────────────────────────────────────────────────────────┘
                        ↓
┌─────────────────────────────────────────────────────────┐
│ Paso 4: Resultados                                      │
├─────────────────────────────────────────────────────────┤
│ 🏆 OPCIÓN RECOMENDADA                                  │
│ ┌──────────────────────────────────────────┐          │
│ │     L      M     Mi     J      V         │          │
│ │ 9  [MAT202] -   [MAT202] -   [MAT202]   │          │
│ │ 11 [PRG301] -   [PRG301] -   [PRG301]   │          │
│ │ 14    -   [BD201] -   [BD201]   -       │          │
│ │                                          │          │
│ │ Total: 5 materias, 20 créditos          │          │
│ │ Amplitud: 9am-3pm                        │          │
│ │ Huecos: 0 horas                          │          │
│ └──────────────────────────────────────────┘          │
│                                                         │
│ 💬 EXPLICACIÓN:                                        │
│ "Te recomiendo esta opción porque:                     │
│  • Cursas PROGRAMACIÓN WEB que reprobaste (prioridad)  │
│  • Cierras tu ciclo de Matemáticas con MAT202         │
│  • Evitas huecos, sales a las 3pm todos los días      │
│  • Compatible con tu horario laboral (tardes libres)"  │
│                                                         │
│ Alternativas: [Ver Opción 2] [Ver Opción 3]           │
│                                                         │
│ Acciones:                                              │
│ [📥 Descargar PDF] [📧 Enviar por email]              │
│ [⭐ Calificar (1-5)] [💾 Guardar para después]        │
└─────────────────────────────────────────────────────────┘
```
```
┌─────────────────────────────────────────────────────────┐
│ 3B. FLUJO: QUÉ MATERIAS TOMAR                          │
├─────────────────────────────────────────────────────────┤
│ (Similar a 3A, pero sin restricción de horario)        │
│                                                         │
│ Input:                                                 │
│ ├─ Kárdex (requerido)                                  │
│ ├─ Mapa Curricular (si no existe en DB)               │
│ └─ Carga deseada (3, 4, 5, 6 materias)                │
│                                                         │
│ Output:                                                │
│ Lista priorizada de materias:                          │
│ 1. ⚠️  Programación Web (REPROBADA - urgente)         │
│ 2. 🔗 Base de Datos (desbloquea 3 materias futuras)   │
│ 3. 📘 Cálculo Diferencial (completa ciclo básico)     │
│ 4. ✅ Inglés III (seriación simple)                   │
│                                                         │
│ Explicación: "Estas 4 materias optimizan tu avance..." │
└─────────────────────────────────────────────────────────┘
```
```
┌─────────────────────────────────────────────────────────┐
│ 3C. FLUJO: CHAT CON TUTOR IA (RAG Inteligente)         │
├─────────────────────────────────────────────────────────┤
│ Interfaz tipo ChatGPT con Búsqueda en Cascada:        │
│                                                         │
│ EJEMPLO 1: Consulta Simple                            │
│ ─────────────────────────────────────────────────────── │
│ 🧑 Estudiante:                                          │
│ "¿Cuál es la fecha límite de inscripciones?"          │
│                                                         │
│ [Sistema: Búsqueda en pgvector → Encontrado]          │
│                                                         │
│ 🤖 Tutor IA:                                            │
│ "Según el calendario académico 2024-2, las            │
│  inscripciones son del 15 al 22 de enero.             │
│  [Fuente: Calendario Académico 2024-2, pág. 3]"       │
│                                                         │
│ EJEMPLO 2: Consulta Compleja                          │
│ ─────────────────────────────────────────────────────── │
│ 🧑 Estudiante:                                          │
│ "¿Puedo inscribir 7 materias?"                        │
│                                                         │
│ [Sistema: Búsqueda en pgvector → Encontrado]          │
│ [Sistema: Consulta kárdex del estudiante → Promedio]  │
│                                                         │
│ 🤖 Tutor IA:                                            │
│ "Según el reglamento de UniCaribe, el máximo es       │
│  6 materias (24 créditos) por semestre regular.       │
│  Excepción: Si tienes promedio >9.0, puedes           │
│  solicitar autorización para 7 materias.              │
│  Tu promedio actual es 8.2, así que te sugiero        │
│  mantener 5-6 materias. [Art. 23, Reglamento]"        │
│                                                         │
│ EJEMPLO 3: Info No Disponible                          │
│ ─────────────────────────────────────────────────────── │
│ 🧑 Estudiante:                                          │
│ "¿Dónde puedo conseguir el libro de Cálculo?"         │
│                                                         │
│ [Sistema: Búsqueda en pgvector → No encontrado]      │
│ [Sistema: Intenta web search → No configurado]        │
│ [Sistema: Usa conocimiento base LLM]                   │
│                                                         │
│ 🤖 Tutor IA:                                            │
│ "No tengo información específica sobre ese libro     │
│  en la base de datos de UniCaribe. Te sugiero:       │
│  1. Consultar con tu profesor                        │
│  2. Revisar la biblioteca universitaria              │
│  3. Preguntar en [enlace coordinación ISW]"          │
│                                                         │
│ ESTRATEGIA DE BÚSQUEDA EN CASCADA:                     │
│ ─────────────────────────────────────────────────────── │
│ Nivel 1: Documentos propios (pgvector RAG)             │
│   → Búsqueda semántica en docs subidos por universidad │
│   → Filtro estricto: universidad_id                    │
│                                                         │
│ Nivel 2: Web Search (opcional, si se configura)       │
│   → Buscar en sitio web oficial de universidad       │
│   → Solo si no se encuentra en Nivel 1              │
│                                                         │
│ Nivel 3: Conocimiento Base del LLM                     │
│   → Respuestas generales educativas                  │
│   → Sin datos específicos de universidad            │
│                                                         │
│ Nivel 4: No tengo información                          │
│   → Reconocer limitación                            │
│   → Sugerir fuentes alternativas                     │
│                                                         │
│ Contexto Disponible:                                   │
│ • Documentos de la universidad (RAG)                  │
│ • Datos del estudiante (kárdex, disponibilidad)      │
│ • Historial de conversación                           │
└─────────────────────────────────────────────────────────┘
```

---

## 💰 Estrategia: Gratis Primero, Escalable Después

### 🎯 Principio Fundamental
**"Prioridad: Resultados confiables. Costo: Lo más bajo posible."**

**Fase 1 - MVP (Desarrollo):**
- 100% Free tier permanente (Gemini, Supabase, Cloud Run)
- Aprovechar trials gratuitos si es necesario
- Sin compromiso de pago

**Fase 2 - Piloto (3 universidades):**
- Mantener free tiers donde sea posible
- Evaluar costos reales de uso
- Usar credits/grants estudiantiles (Google Cloud $300, GitHub Student)

**Fase 3 - Producción (Futuro):**
- Migrar a modelos pagos solo si:
  1. Volumen excede free tier
  2. Calidad/velocidad lo requiere
  3. Hay ingresos para cubrir costos

**Filosofía:**
❌ NO sacrificar calidad por ser gratis al 100%
✅ SÍ usar trials/credits para desarrollo
✅ SÍ tener plan de escalamiento claro

---

### ☁️ Servicios Cloud (Estrategia por Fases)

**Servicios 100% Gratis (Permanentes):**

| Servicio | Free Tier | Límite Mensual | Uso en Proyecto |
|----------|-----------|----------------|-----------------|
| **Google Cloud Run** | ✅ Gratis | 2M requests, 360K GB-segundos | Backend API |
| **Google Cloud Storage** | ✅ Gratis | 5GB almacenamiento | Imágenes estudiantes |
| **Google Gemini 1.5 Flash** | ✅ Gratis | 15 req/min, 1M tokens/día | LLM principal |
| **Google Gemini 1.5 Pro** | ✅ Gratis | 2 req/min (suficiente) | Vision API |
| **Supabase PostgreSQL** | ✅ Gratis | 500MB DB, 2GB transferencia | Base de datos |
| **Upstash Redis** | ✅ Gratis | 10K commands/día | Cache |
| **Vercel** | ✅ Gratis | 100GB bandwidth | Frontend |
| **GitHub Actions** | ✅ Gratis | 2000 min/mes | CI/CD |
| **LangSmith** | ✅ Gratis | 5K traces/mes | Debugging agente |
| **Sentry** | ✅ Gratis | 5K events/mes | Error tracking |

**Costo Total Mensual MVP: $0 USD** ✅

**Créditos/Trials Disponibles (Desarrollo):**

| Recurso | Beneficio | Duración | Uso |
|---------|-----------|----------|-----|
| Google Cloud Free Trial | $300 créditos | 90 días | Backup Cloud Run si excede free tier |
| GitHub Student Pack | Varios servicios | 2 años | Copilot, Azure credits |
| OpenAI Free Trial | $5 credits | Limitado | Testing comparativo GPT-4 vs Gemini |
| Anthropic Claude | API key gratis | Limitado | Testing alternativo si Gemini falla |

**Estrategia:**
- MVP usa solo free tier permanente
- Trials se usan para **testing** y **comparación de calidad**
- Si un modelo pago da resultados significativamente mejores → documentar para decisión futura

---

### 🚫 Servicios a EVITAR (No gratis o límites muy bajos)

| Servicio | Por qué NO |
|----------|------------|
| OpenAI GPT-4 | Sin free tier ($0.01/1K tokens) |
| AWS (sin estudiante) | Free tier 12 meses, luego paga |
| Pinecone | Solo 1 índice gratis (limitado) |
| MongoDB Atlas | 512MB límite (muy poco) |
| Heroku | Ya no tiene free tier |

---

### 🔑 APIs Gratuitas Confirmadas
```python
# ✅ Google Generative AI (GRATIS)
from langchain_google_genai import ChatGoogleGenerativeAI

llm = ChatGoogleGenerativeAI(
    model="gemini-1.5-flash",  # 15 req/min GRATIS
    google_api_key=settings.google_api_key
)

# ✅ Google Embeddings (GRATIS)
from langchain_google_genai import GoogleGenerativeAIEmbeddings

embeddings = GoogleGenerativeAIEmbeddings(
    model="models/embedding-001",  # GRATIS
    google_api_key=settings.google_api_key
)

# ✅ Supabase PostgreSQL (GRATIS)
DATABASE_URL = "postgresql://..."  # 500MB gratis
```

---

### 📊 Monitoreo de Límites

**Dashboard de uso (crear endpoint):**
```python
@app.get("/admin/usage")
async def get_usage_stats():
    """Monitorear que no excedamos free tiers"""
    return {
        "gemini_calls_today": get_gemini_usage(),
        "storage_gb": get_storage_usage(),
        "db_size_mb": get_db_size(),
        "monthly_requests": get_request_count()
    }
```

**Alertas:**
- Si Gemini > 10K calls/día → Warning
- Si Storage > 4GB → Warning
- Si DB > 400MB → Limpiar sesiones antiguas

---

## 🎓 Tecnologías de Alto Valor para CV

### 🔥 Top Prioridad (Mencionables en entrevistas)

**1. LangChain + LangGraph**
```
Por qué: Framework #1 para IA empresarial en 2024
Mención CV: "Desarrollo de agentes conversacionales multi-paso 
con LangGraph para automatización de procesos académicos"
Keywords: LangChain, LangGraph, AI Agents, Tool Calling
```

**2. Google Cloud Platform (GCP)**
```
Por qué: Top 3 cloud provider, menos saturado que AWS
Mención CV: "Deploy de aplicaciones containerizadas en Google 
Cloud Run con arquitectura serverless"
Keywords: GCP, Cloud Run, Cloud Storage, Serverless
```

**3. FastAPI**
```
Por qué: Framework Python más demandado en startups
Mención CV: "Desarrollo de APIs REST async con FastAPI, 
logrando <100ms response time"
Keywords: FastAPI, Async Python, REST APIs, High Performance
```

**4. Docker + Docker Compose**
```
Por qué: Estándar de industria para contenedores
Mención CV: "Containerización de microservicios con Docker 
y orquestación local con Docker Compose"
Keywords: Docker, Containerization, Microservices
```

**5. PostgreSQL + pgvector**
```
Por qué: DB #1 empresarial + extensión ML trending
Mención CV: "Implementación de RAG con PostgreSQL pgvector 
para búsqueda semántica en documentos"
Keywords: PostgreSQL, Vector Database, RAG, Embeddings
```

**6. Multimodal AI (Vision)**
```
Por qué: Skill muy demandado post-GPT-4V
Mención CV: "Procesamiento de documentos académicos usando 
Gemini Vision API con >90% accuracy"
Keywords: Vision AI, Multimodal LLMs, Document Processing
```

---

### 📝 Cómo Presentarlo en CV

**Sección Proyectos:**
```
🤖 Sistema Multi-Universidad de Tutoría IA | Dic 2024
Stack: Python, FastAPI, LangChain, Docker, GCP, PostgreSQL

- Desarrollé agente conversacional con LangGraph capaz de procesar
  documentos académicos (imágenes) usando Gemini Vision API
  
- Implementé arquitectura multi-tenant serverless en Google Cloud Run,
  soportando múltiples universidades con aislamiento de datos
  
- Diseñé pipeline de RAG con pgvector para búsqueda semántica en
  reglamentos universitarios (embeddings + PostgreSQL)
  
- Containericé aplicación con Docker, logrando despliegue reproducible
  en <5 minutos desde git clone
  
- Integré sistema de optimización de horarios que reduce conflictos
  en 85% vs selección manual de estudiantes

🔗 GitHub: github.com/usuario/proyecto-terminal
🔗 Demo: tutorai.unicaribe.com
```

---

### 🎤 Talking Points para Entrevistas

**Pregunta: "Cuéntame sobre un proyecto reciente"**
```
Respuesta preparada:

"Desarrollé un sistema de tutoría inteligente multi-universidad 
que ayuda a estudiantes a armar horarios académicos optimizados.

El reto técnico interesante fue que las universidades tienen 
formatos de documentos muy variados - PDFs, imágenes, tablas 
complejas. En lugar de hacer parsers específicos, usé Gemini 
Vision API (multimodal LLM) para extraer datos de cualquier 
formato con prompts estructurados.

Arquitectónicamente, implementé multi-tenancy en PostgreSQL 
donde cada universidad es un tenant aislado, con su propio 
conjunto de embeddings en pgvector para RAG. Esto me permitió 
escalar de 1 a N universidades sin cambiar código.

Para el agente, usé LangGraph en vez de LangChain básico porque 
necesitaba un grafo de decisión complejo: primero analizar 
documentos (tool vision), luego filtrar materias elegibles 
(tool prerrequisitos), luego generar combinaciones (tool scheduler), 
y finalmente explicar en lenguaje natural.

Lo desplegué en Cloud Run (serverless) con Docker, y todo el 
stack es gratis - importante para un proyecto académico pero 
también aprendí a optimizar costos cloud.

El resultado: estudiantes arman horarios en 30 segundos vs 
2+ horas manual, y el accuracy de extracción de datos es >90%."
```

**Follow-up esperado: "¿Qué desafíos tuviste?"**
```
"El mayor desafío fue la calidad variable de imágenes. Algunos 
estudiantes suben fotos de celular mal iluminadas. Implementé 
validación pre-procesamiento con Pillow para detectar calidad 
y rechazar imágenes muy malas antes de mandarlas a Gemini, 
ahorrando API calls.

Otro desafío: los LLMs a veces 'alucinan' datos en documentos. 
Para mitigarlo, uso temperature=0 y prompts muy específicos 
que piden JSON estructurado con validación Pydantic después."
```

---

## 🐋 Estrategia Docker (Cloud-Ready)

### Por Qué Docker es Crítico

**1. Reproducibilidad**
```bash
# Cualquier compañero del equipo:
git clone repo
docker compose up -d
# → Sistema funcional en 3 minutos
```

**2. Paridad Dev/Prod**
```
Dev Local (Ubuntu VM):  Docker Compose
Producción (GCP):       Cloud Run (usa mismo Dockerfile)
→ "Works on my machine" eliminado
```

**3. Portabilidad**
```
Universidad dice: "Queremos hospearlo en nuestro servidor"
→ Les das docker-compose.yml
→ Funciona en cualquier máquina con Docker
```

---

### 🏗️ Arquitectura Docker Multi-Stage

**Optimización del Dockerfile:**
```dockerfile
# ===== STAGE 1: Builder =====
FROM python:3.11-slim as builder

WORKDIR /app

# Instalar dependencias de compilación
RUN apt-get update && apt-get install -y --no-install-recommends \
    gcc \
    && rm -rf /var/lib/apt/lists/*

# Copiar solo requirements primero (cache layer)
COPY requirements.txt .
RUN pip wheel --no-cache-dir --no-deps --wheel-dir /app/wheels -r requirements.txt

# ===== STAGE 2: Runtime =====
FROM python:3.11-slim

WORKDIR /app

# Copiar wheels del builder
COPY --from=builder /app/wheels /wheels
COPY --from=builder /app/requirements.txt .

# Instalar solo runtime dependencies
RUN apt-get update && apt-get install -y --no-install-recommends \
    postgresql-client \
    && rm -rf /var/lib/apt/lists/* \
    && pip install --no-cache /wheels/*

# Copiar código
COPY . .

# Usuario no-root (seguridad)
RUN useradd -m -u 1000 appuser && chown -R appuser:appuser /app
USER appuser

EXPOSE 8000

CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
```

**Beneficios:**
- ✅ Imagen final 40% más pequeña
- ✅ Builds más rápidos (cache de layers)
- ✅ Más seguro (usuario no-root)
- ✅ Menos superficie de ataque

---

### 📦 docker-compose.yml Optimizado
```yaml
version: '3.8'

services:
  # PostgreSQL con pgvector
  postgres:
    image: pgvector/pgvector:pg15
    container_name: tutor_ia_db
    environment:
      POSTGRES_DB: tutor_ia
      POSTGRES_USER: postgres
      POSTGRES_PASSWORD: ${POSTGRES_PASSWORD:-postgres_dev}
    ports:
      - "5432:5432"
    volumes:
      - postgres_data:/var/lib/postgresql/data
      - ./init.sql:/docker-entrypoint-initdb.d/init.sql  # Init scripts
    healthcheck:
      test: ["CMD-SHELL", "pg_isready -U postgres"]
      interval: 10s
      timeout: 5s
      retries: 5
    networks:
      - tutor_network

  # Redis para cache
  redis:
    image: redis:7-alpine
    container_name: tutor_ia_cache
    ports:
      - "6379:6379"
    volumes:
      - redis_data:/data
    healthcheck:
      test: ["CMD", "redis-cli", "ping"]
      interval: 10s
      timeout: 3s
      retries: 5
    networks:
      - tutor_network

  # Backend FastAPI
  backend:
    build:
      context: ./backend
      dockerfile: Dockerfile
    container_name: tutor_ia_api
    command: uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload
    volumes:
      - ./backend:/app
      - ./uploads:/uploads  # Imágenes temporales
    ports:
      - "8000:8000"
    environment:
      DATABASE_URL: postgresql://postgres:${POSTGRES_PASSWORD:-postgres_dev}@postgres:5432/tutor_ia
      REDIS_URL: redis://redis:6379
      GOOGLE_API_KEY: ${GOOGLE_API_KEY}
      ENVIRONMENT: ${ENVIRONMENT:-development}
    depends_on:
      postgres:
        condition: service_healthy
      redis:
        condition: service_healthy
    networks:
      - tutor_network
    restart: unless-stopped

volumes:
  postgres_data:
    driver: local
  redis_data:
    driver: local

networks:
  tutor_network:
    driver: bridge
```

**Features clave:**
- ✅ Healthchecks (espera a que DB esté ready)
- ✅ Restart policies (auto-recovery)
- ✅ Variables de entorno seguras
- ✅ Volúmenes persistentes
- ✅ Network isolation

---

### 🚀 Deploy a Google Cloud Run

**Preparación:**
```dockerfile
# backend/Dockerfile.prod (para producción)
FROM python:3.11-slim

WORKDIR /app

# Instalar dependencias
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copiar código
COPY . .

# Puerto de Cloud Run
ENV PORT=8080
EXPOSE 8080

# Usuario no-root
RUN useradd -m -u 1000 appuser && chown -R appuser:appuser /app
USER appuser

# Uvicorn con workers para producción
CMD uvicorn app.main:app --host 0.0.0.0 --port ${PORT} --workers 4
```

**Deploy script:**
```bash
#!/bin/bash
# deploy.sh

PROJECT_ID="tutor-ia-prod"
SERVICE_NAME="tutor-ia-api"
REGION="us-central1"

# Build y push a Container Registry
gcloud builds submit --tag gcr.io/${PROJECT_ID}/${SERVICE_NAME}

# Deploy a Cloud Run
gcloud run deploy ${SERVICE_NAME} \
  --image gcr.io/${PROJECT_ID}/${SERVICE_NAME} \
  --platform managed \
  --region ${REGION} \
  --allow-unauthenticated \
  --set-env-vars="DATABASE_URL=${DATABASE_URL},GOOGLE_API_KEY=${GOOGLE_API_KEY}" \
  --memory 1Gi \
  --cpu 2 \
  --max-instances 10 \
  --timeout 60s

echo "✅ Deployed to: $(gcloud run services describe ${SERVICE_NAME} --region ${REGION} --format 'value(status.url)')"
```

---

### 📊 Comparativa: Local vs Cloud

| Aspecto | Docker Compose Local | Google Cloud Run |
|---------|---------------------|------------------|
| **Costo** | $0 (tu PC) | $0 (free tier) |
| **Setup** | 5 min | 10 min primera vez |
| **Escalabilidad** | 1 instancia | Auto-scale a 10 |
| **Disponibilidad** | Solo cuando tu PC está prendida | 24/7 |
| **URL** | localhost:8000 | https://tutor-ia-xxx.run.app |
| **SSL** | No | ✅ Gratis automático |
| **CI/CD** | Manual | ✅ GitHub Actions |

**Estrategia Recomendada:**
1. **Desarrollo:** Docker Compose local (toda la semana)
2. **Demos al profesor:** Cloud Run (deploy antes de clase)
3. **Producción MVP:** Cloud Run (últimas 2 semanas)

---

## 🎯 Checklist Final: "MVP Cloud-Ready"

### Semana 12 (Entrega Final)
```
✅ Funcionalidad
  ├─ Vision tool procesa oferta/mapa/kardex
  ├─ Schedule builder genera 3 opciones de horario
  ├─ RAG responde preguntas de universidad
  └─ Frontend básico funcional

✅ Infraestructura
  ├─ Dockerizado (compose + Dockerfile)
  ├─ Deploy en Cloud Run funcional
  ├─ DB en Supabase con datos de prueba
  ├─ Storage en GCS para imágenes
  └─ Monitoring básico (logs)

✅ Documentación
  ├─ README.md completo con setup
  ├─ API docs automática (FastAPI /docs)
  ├─ Diagrama de arquitectura
  └─ Video demo (3-5 min)

✅ GitHub
  ├─ Código limpio y comentado
  ├─ Commits descriptivos (>50)
  ├─ Branches y PRs (workflow colaborativo)
  └─ Issues cerrados

✅ Presentación
  ├─ Slides con arquitectura
  ├─ Demo en vivo (Cloud Run URL)
  ├─ Métricas de rendimiento
  └─ Lecciones aprendidas
```

---

## 💡 Pro Tips: Impresionar en Entrevistas

### 1. Menciona Trade-offs
```
"Elegí Gemini sobre GPT-4 no solo por costo ($0 vs $X), 
sino porque Gemini tiene mejor performance en documentos 
en español según mis pruebas. Hice benchmark A/B."
```

### 2. Habla de Observabilidad
```
"Implementé LangSmith tracing para debuggear el agente. 
Por ejemplo, descubrí que 30% de fallos venían de prompts 
mal formateados, no del modelo."
```

### 3. Métricas Concretas
```
"El sistema procesa una consulta en promedio 22 segundos:
  - 8s extracción de imagen (Gemini Vision)
  - 12s generación de horarios (algoritmo)
  - 2s respuesta LLM
Identifiqué que el bottleneck es Vision API, así que 
implementé caché de documentos procesados."
```

### 4. Menciona Escalabilidad
```
"Arquitectura multi-tenant permite agregar nuevas universidades 
sin código nuevo. Solo suben sus documentos y el RAG se auto-configura."
```

---

## 🚨 Red Flags a Evitar

### ❌ NO digas:
- "No sé cómo funciona Docker, solo lo usé"
- "El profesor nos dio el código"
- "Gemini a veces falla pero no sé por qué"
- "Solo trabajé en el frontend"

### ✅ SÍ di:
- "Dockericé la app para garantizar paridad dev/prod"
- "Diseñamos la arquitectura basándonos en research papers de..."
- "Cuando Gemini fallaba, debuggeé con LangSmith y ajusté prompts"
- "Me encargué del backend pero entiendo toda la arquitectura"

---

**Última Actualización:** Diciembre 2024  
**Filosofía:** Gratis, Cloud-Native, Enterprise-Grade, CV-Worthy
