# 🏗️ Arquitectura y Decisiones Técnicas - Tutor IA

> Documento técnico que explica el proyecto, tecnologías utilizadas y las decisiones de diseño.

---

## 📋 Resumen del Proyecto

**Nombre:** Tutor IA - Sistema de Tutoría Académica Inteligente

**Objetivo:** Plataforma SaaS multi-universidad que ayuda a estudiantes a:
1. **Armar horarios óptimos** basados en disponibilidad y prerrequisitos
2. **Seleccionar materias** respetando el mapa curricular
3. **Consultar información** de su universidad mediante chat con IA

**Problema que Resuelve:**
- Estudiantes pierden 2+ horas armando horarios manualmente
- Cometen errores de prerrequisitos
- No tienen acceso fácil a información institucional

**Tipo de Sistema:** Multi-tenant (una instancia, múltiples universidades)

---

## 🏛️ Arquitectura General

```
┌─────────────────────────────────────────────────────────────────┐
│                         CLIENTES                                │
│  ┌─────────────────┐              ┌─────────────────┐          │
│  │  Portal         │              │  Panel Admin    │          │
│  │  Estudiantes    │              │  Universidades  │          │
│  │  :8501          │              │  :8502          │          │
│  └────────┬────────┘              └────────┬────────┘          │
└───────────┼────────────────────────────────┼────────────────────┘
            │                                │
            └───────────────┬────────────────┘
                            ▼
┌─────────────────────────────────────────────────────────────────┐
│                      BACKEND (FastAPI)                          │
│                         :8000                                   │
│                                                                 │
│  ┌─────────────────────────────────────────────────────────┐   │
│  │                   API Layer (/api/v1/)                   │   │
│  │  ┌────────┐ ┌────────┐ ┌────────┐ ┌────────┐ ┌───────┐  │   │
│  │  │  auth  │ │ vision │ │schedule│ │  rag   │ │ admin │  │   │
│  │  └────────┘ └────────┘ └────────┘ └────────┘ └───────┘  │   │
│  └─────────────────────────────────────────────────────────┘   │
│                              │                                  │
│  ┌─────────────────────────────────────────────────────────┐   │
│  │                  LangGraph Agent                         │   │
│  │                                                          │   │
│  │   ┌──────────────┐ ┌──────────────┐ ┌──────────────┐    │   │
│  │   │  VisionTool  │ │ ScheduleTool │ │   RAGTool    │    │   │
│  │   │              │ │              │ │              │    │   │
│  │   │ Extrae datos │ │ Genera       │ │ Busca info   │    │   │
│  │   │ de imágenes  │ │ horarios     │ │ universidad  │    │   │
│  │   └──────┬───────┘ └──────┬───────┘ └──────┬───────┘    │   │
│  │          │                │                │             │   │
│  │          └────────────────┼────────────────┘             │   │
│  │                           ▼                              │   │
│  │              ┌─────────────────────────┐                 │   │
│  │              │    Google Gemini API    │                 │   │
│  │              │   (Flash + Vision)      │                 │   │
│  │              └─────────────────────────┘                 │   │
│  └─────────────────────────────────────────────────────────┘   │
│                              │                                  │
│  ┌─────────────────────────────────────────────────────────┐   │
│  │                   Services Layer                         │   │
│  │  ┌──────────┐ ┌──────────┐ ┌──────────┐ ┌────────────┐  │   │
│  │  │   auth   │ │  vision  │ │ schedule │ │   cache    │  │   │
│  │  │ service  │ │ service  │ │ service  │ │  service   │  │   │
│  │  └──────────┘ └──────────┘ └──────────┘ └────────────┘  │   │
│  └─────────────────────────────────────────────────────────┘   │
└─────────────────────────┬───────────────────────────────────────┘
                          │
        ┌─────────────────┼─────────────────┐
        ▼                 ▼                 ▼
┌──────────────┐  ┌──────────────┐  ┌──────────────┐
│  PostgreSQL  │  │    Redis     │  │   pgvector   │
│     15       │  │      7       │  │  embeddings  │
│              │  │              │  │              │
│  - usuarios  │  │  - cache     │  │  - búsqueda  │
│  - carreras  │  │  - sesiones  │  │    semántica │
│  - sesiones  │  │  - rate limit│  │              │
└──────────────┘  └──────────────┘  └──────────────┘
```

---

## 🛠️ Stack Tecnológico y Justificación

### Backend

| Tecnología | Versión | ¿Por qué? |
|------------|---------|-----------|
| **Python** | 3.11 | Lenguaje estándar para IA, ecosistema maduro |
| **FastAPI** | 0.109 | Async nativo, validación automática, docs OpenAPI gratis |
| **Pydantic** | 2.5 | Validación de datos type-safe, serialización JSON |
| **SQLAlchemy** | 2.0 | ORM maduro, soporte async, compatible con Alembic |
| **Alembic** | 1.13 | Migraciones versionadas de BD |

**Decisión clave:** FastAPI sobre Flask/Django
- Flask: Muy simple, no tiene async nativo
- Django: Demasiado opinionated, REST no es su fuerte
- **FastAPI:** Async, validación automática, performance excelente

### Inteligencia Artificial

| Tecnología | Versión | ¿Por qué? |
|------------|---------|-----------|
| **LangChain** | 0.1.0 | Framework estándar para aplicaciones LLM |
| **LangGraph** | 0.0.20 | Orquestación de agentes con estado y flujos complejos |
| **Google Gemini** | 1.5 Flash | Gratis, rápido, multimodal (texto + visión) |
| **pgvector** | 0.2.4 | Embeddings en PostgreSQL, no necesita DB adicional |

**Decisión clave:** LangGraph sobre LangChain básico
```
LangChain básico:
  Usuario → LLM → Respuesta (lineal)

LangGraph:
  Usuario → [Analizar] → [¿Tipo consulta?]
                              ├── Horario → VisionTool → ScheduleTool → Respuesta
                              ├── Info → RAGTool → Respuesta
                              └── Chat → LLM directo → Respuesta
```
LangGraph permite flujos condicionales con estado, necesario para nuestro agente multi-herramienta.

**Decisión clave:** Gemini sobre GPT-4/Claude
- GPT-4: $0.03/1K tokens, sin tier gratis
- Claude: $0.015/1K tokens, tier gratis limitado
- **Gemini Flash:** GRATIS 15 req/min, 1M tokens/día, visión incluida

### Base de Datos

| Tecnología | Versión | ¿Por qué? |
|------------|---------|-----------|
| **PostgreSQL** | 15 | Robusto, JSONB para datos flexibles, extensible |
| **pgvector** | ext | Embeddings vectoriales sin DB adicional (vs Pinecone) |
| **Redis** | 7 | Cache ultra-rápido, TTL nativo |

**Decisión clave:** pgvector sobre Pinecone/Weaviate
- Pinecone: Servicio separado, costo adicional, límite gratis pequeño
- Weaviate: Complejo de configurar, overkill para nuestro caso
- **pgvector:** Ya tenemos PostgreSQL, 0 costo adicional, queries SQL normales

**Decisión clave:** Redis para cache
- Sin cache: Cada request = query a DB + llamada a Gemini
- Con cache: Respuestas repetidas en 3ms vs 300ms
- **Resultado:** 60% mejora en tiempos de respuesta

### Frontend

| Tecnología | Versión | ¿Por qué? |
|------------|---------|-----------|
| **Streamlit** | 1.31 | Prototipado rápido, Python puro, ideal para MVP |

**Decisión clave:** Streamlit sobre React/Next.js
- React: Requiere frontend developer, tiempo de desarrollo 3x
- Next.js: Excelente pero overkill para MVP académico
- **Streamlit:** Prototipo funcional en horas, mismo lenguaje que backend

**Trade-off aceptado:** Streamlit tiene limitaciones de UI/UX, pero para un MVP académico es suficiente. Migración a Next.js planeada para producción.

### DevOps

| Tecnología | ¿Por qué? |
|------------|-----------|
| **Docker** | Reproducibilidad, "works on my machine" eliminado |
| **Docker Compose** | Orquestación simple de 5 servicios |
| **GitHub Actions** | CI/CD gratuito para repos públicos |

---

## 🏢 Arquitectura Multi-Tenant

### Estrategia: Shared Database, Shared Schema

```
┌─────────────────────────────────────────────────────────┐
│                    PostgreSQL                           │
│  ┌─────────────────────────────────────────────────┐   │
│  │  tabla: universidades                            │   │
│  │  ├── id: uuid (PK)                               │   │
│  │  ├── nombre: "Universidad del Caribe"            │   │
│  │  └── slug: "unicaribe"                           │   │
│  └─────────────────────────────────────────────────┘   │
│                         │                               │
│                         ▼ FK                            │
│  ┌─────────────────────────────────────────────────┐   │
│  │  tabla: estudiantes                              │   │
│  │  ├── id: uuid                                    │   │
│  │  ├── universidad_id: uuid (FK) ← FILTRO SIEMPRE │   │
│  │  └── email: "juan@unicaribe.mx"                 │   │
│  └─────────────────────────────────────────────────┘   │
│                                                         │
│  REGLA DE ORO: Toda query incluye WHERE universidad_id │
└─────────────────────────────────────────────────────────┘
```

**¿Por qué shared schema?**
- Database-per-tenant: Complejo de mantener, migraciones por tenant
- Schema-per-tenant: Mejor aislamiento pero más complejo
- **Shared schema:** Simple, un WHERE extra, suficiente para MVP

**Implementación:**
```python
# ✅ SIEMPRE filtrar por universidad
estudiantes = await db.execute(
    select(Estudiante).where(
        Estudiante.universidad_id == current_user.universidad_id
    )
)

# ❌ NUNCA queries globales
estudiantes = await db.execute(select(Estudiante))  # PELIGRO
```

---

## 🤖 Diseño del Agente IA

### Filosofía: IA para Flexibilidad, Algoritmos para Confiabilidad

```
┌─────────────────────────────────────────────────────────┐
│                   PRINCIPIO RECTOR                      │
├─────────────────────────────────────────────────────────┤
│  LLM/IA:      Input flexible + Explicaciones naturales │
│  Algoritmos:  Validación estricta + Lógica confiable   │
└─────────────────────────────────────────────────────────┘
```

**Ejemplo: Generación de Horarios**

```
1. EXTRACCIÓN (IA - Flexible)
   └── VisionTool procesa imagen de oferta académica
   └── Gemini extrae: materias, horarios, profesores
   └── Output: JSON estructurado
   
2. VALIDACIÓN (Algoritmo - Estricto)
   └── Pydantic valida estructura del JSON
   └── Verificar prerrequisitos con grafo (networkx)
   └── Detectar conflictos de horario (intervalos)
   
3. OPTIMIZACIÓN (Algoritmo - Confiable)
   └── Generar combinaciones válidas (backtracking)
   └── Rankear por criterios (huecos, preferencias)
   └── Seleccionar top 3 opciones
   
4. EXPLICACIÓN (IA - UX)
   └── Gemini explica en lenguaje natural
   └── "Te recomiendo esta opción porque..."
```

**¿Por qué no usar solo IA?**
```python
# ❌ MAL: Dejar que el LLM decida prerrequisitos
respuesta = llm.invoke("¿Puede Juan tomar Cálculo II?")
# El LLM puede alucinar: "Sí, claro que puede"

# ✅ BIEN: Algoritmo decide, LLM explica
puede_tomar = grafo.cumple_prerrequisitos("CAL2", kardex_juan)
if puede_tomar:
    explicacion = llm.invoke("Explica por qué Juan puede tomar Cálculo II")
else:
    explicacion = llm.invoke("Explica por qué Juan NO puede tomar Cálculo II")
```

---

## 💾 Estrategia de Cache

### Niveles de Cache

```
┌─────────────────────────────────────────────────────────┐
│                    ESTRATEGIA DE CACHE                  │
├─────────────────────────────────────────────────────────┤
│  TTL Corto (1 min):   Datos que cambian frecuentemente │
│  TTL Medio (5 min):   Listados, dashboard               │
│  TTL Largo (1 hora):  Configuraciones, carreras         │
│  TTL Día (24 horas):  Respuestas RAG, embeddings        │
└─────────────────────────────────────────────────────────┘
```

### Implementación

```python
# Patrón: Cache-Aside con invalidación
class CacheService:
    TTL_SHORT = 60      # 1 minuto
    TTL_MEDIUM = 300    # 5 minutos
    TTL_LONG = 3600     # 1 hora
    TTL_DAY = 86400     # 24 horas
    
    async def get_or_set(self, key, fetch_func, ttl):
        # 1. Intentar obtener de cache
        cached = await self.get(key)
        if cached:
            return cached
        
        # 2. Si no está, obtener de DB
        data = await fetch_func()
        
        # 3. Guardar en cache
        await self.set(key, data, ttl)
        
        return data
```

### Invalidación

```python
# Cuando se crea/actualiza/elimina → invalidar cache relacionado
@router.post("/carreras")
async def create_carrera(...):
    # Crear en DB
    carrera = await crear_carrera(db, data)
    
    # Invalidar cache
    await cache.invalidate_pattern(f"tutor_ia:carreras:{universidad_id}:*")
    
    return carrera
```

**Resultado medido:** 60% mejora en tiempos de respuesta (9.8ms → 3.8ms)

---

## 🔐 Seguridad

### Autenticación JWT

```
┌─────────────────────────────────────────────────────────┐
│  POST /auth/login                                       │
│  Body: { email, password }                              │
│                                                         │
│  1. Verificar credenciales en DB                        │
│  2. Generar JWT con payload:                            │
│     {                                                   │
│       "sub": "user_id",                                 │
│       "universidad_id": "uuid",                         │
│       "role": "estudiante|admin",                       │
│       "exp": timestamp                                  │
│     }                                                   │
│  3. Retornar: { access_token, token_type }              │
└─────────────────────────────────────────────────────────┘
```

### Protección de Endpoints

```python
# Dependency injection para autenticación
@router.get("/mis-datos")
async def get_mis_datos(
    current_user: Estudiante = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    # current_user ya está validado y tiene universidad_id
    return await obtener_datos(db, current_user.id)
```

---

## 📊 Modelo de Datos Simplificado

```
┌─────────────────┐     ┌─────────────────┐
│  Universidad    │────<│    Carrera      │
│  - id           │     │  - id           │
│  - nombre       │     │  - nombre       │
│  - slug         │     │  - plan_estudios│
│  - config       │     │  - universidad_id│
└─────────────────┘     └─────────────────┘
        │                       │
        │                       │
        ▼                       ▼
┌─────────────────┐     ┌─────────────────┐
│   Estudiante    │     │ UniversidadInfo │
│  - id           │     │  - id           │
│  - email        │     │  - tipo         │
│  - carrera_id   │     │  - contenido    │
│  - universidad_id│    │  - embedding    │
└─────────────────┘     │  - universidad_id│
        │               └─────────────────┘
        ▼
┌─────────────────┐
│SesionConsultoria│
│  - id           │
│  - tipo         │
│  - resultado    │
│  - estudiante_id│
└─────────────────┘
```

---

## 💰 Estrategia de Costos

### Todo Gratis para MVP

| Servicio | Tier Gratis | Límite |
|----------|-------------|--------|
| Google Gemini | ✅ | 15 req/min, 1M tokens/día |
| Supabase PostgreSQL | ✅ | 500MB DB |
| Vercel (futuro) | ✅ | 100GB bandwidth |
| GitHub Actions | ✅ | 2000 min/mes |

### Estimación para Producción

```
1000 estudiantes activos:
- ~5000 consultas/día
- ~500K tokens Gemini/día (dentro de límite gratis)
- ~100MB DB
- ~1GB storage imágenes

Costo estimado: $0/mes (dentro de free tiers)
```

---

## 🚀 Decisiones Pendientes para Producción

1. **Frontend:** Migrar de Streamlit a Next.js para mejor UX
2. **Auth:** Implementar refresh tokens y cookies HTTP-only
3. **Observabilidad:** Agregar Sentry para error tracking
4. **Monitoreo:** Dashboard de métricas con Grafana
5. **CDN:** CloudFlare para assets estáticos
6. **CI/CD:** Pipeline completo con tests y deploy automático

---

## 📚 Referencias

- [FastAPI Documentation](https://fastapi.tiangolo.com/)
- [LangChain Docs](https://python.langchain.com/)
- [LangGraph Guide](https://langchain-ai.github.io/langgraph/)
- [pgvector](https://github.com/pgvector/pgvector)
- [Google Gemini API](https://ai.google.dev/docs)

---

**Última actualización:** Enero 2025
**Equipo:** David Jauregui, Oscar Ruiz, Gustavo Meraz
**Universidad:** Universidad del Caribe
