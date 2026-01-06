# 🎓 Tutor IA - Sistema de Tutoría Académica Inteligente

[![Python 3.11](https://img.shields.io/badge/Python-3.11-blue.svg)](https://www.python.org/)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.109-green.svg)](https://fastapi.tiangolo.com/)
[![Docker](https://img.shields.io/badge/Docker-Ready-blue.svg)](https://www.docker.com/)
[![LangChain](https://img.shields.io/badge/LangChain-0.1.0-orange.svg)](https://python.langchain.com/)

> Sistema SaaS multi-universidad que ayuda a estudiantes a optimizar su inscripción académica usando Inteligencia Artificial.

---

## 🌟 Características

- 🤖 **Agente Conversacional** - Chat inteligente con LangGraph
- 👁️ **Análisis de Documentos** - Extrae datos de Kárdex, Ofertas y Mapas Curriculares con Gemini Vision
- 📅 **Optimización de Horarios** - Genera y rankea combinaciones de horarios
- 📚 **RAG Universitario** - Responde preguntas sobre la universidad con embeddings
- 🏢 **Multi-Tenant** - Soporta múltiples universidades aisladas

---

## 🚀 Inicio Rápido

### Prerrequisitos
- Docker 24.0+
- Docker Compose 2.20+
- Google AI API Key ([obtener aquí](https://aistudio.google.com/app/apikey))

### Instalación

```bash
# 1. Clonar repositorio
git clone https://github.com/tu-usuario/ProyectoTerminal.git
cd ProyectoTerminal

# 2. Configurar variables de entorno
cp backend/.env.example backend/.env
# Editar backend/.env y agregar GOOGLE_API_KEY

# 3. Levantar servicios
docker compose up -d --build

# 4. Ejecutar migraciones
docker compose exec backend alembic upgrade head

# 5. Abrir aplicación
open http://localhost:8501
```

📖 **[Guía completa de instalación →](docs/QUICK_START.md)**

---

## 🖥️ URLs

| Servicio | URL | Descripción |
|----------|-----|-------------|
| Frontend | http://localhost:8501 | Interfaz Streamlit |
| API Docs | http://localhost:8000/docs | Swagger UI |
| Health | http://localhost:8000/health | Estado del sistema |

---

## 🏗️ Arquitectura

```
┌─────────────────────────────────────────────────────────┐
│                    Frontend (Streamlit)                 │
│                    http://localhost:8501                │
└─────────────────────────┬───────────────────────────────┘
                          │
┌─────────────────────────▼───────────────────────────────┐
│                  Backend (FastAPI)                      │
│                  http://localhost:8000                  │
│                                                         │
│  ┌─────────────────────────────────────────────────┐   │
│  │              LangGraph Agent                     │   │
│  │  ┌──────────┐ ┌──────────┐ ┌──────────┐        │   │
│  │  │  Vision  │ │ Schedule │ │   RAG    │        │   │
│  │  │   Tool   │ │   Tool   │ │   Tool   │        │   │
│  │  └────┬─────┘ └────┬─────┘ └────┬─────┘        │   │
│  └───────┼────────────┼────────────┼───────────────┘   │
│          │            │            │                    │
│          ▼            ▼            ▼                    │
│  ┌──────────────────────────────────────────────┐      │
│  │            Gemini 2.5 Flash API              │      │
│  └──────────────────────────────────────────────┘      │
└─────────────────────────┬───────────────────────────────┘
                          │
          ┌───────────────┼───────────────┐
          ▼               ▼               ▼
    ┌──────────┐   ┌──────────┐   ┌──────────┐
    │PostgreSQL│   │  Redis   │   │ pgvector │
    │    15    │   │    7     │   │embeddings│
    └──────────┘   └──────────┘   └──────────┘
```

---

## 📁 Estructura del Proyecto

```
ProyectoTerminal/
├── backend/                 # API FastAPI + LangChain
│   ├── app/
│   │   ├── agents/         # Agente LangGraph
│   │   ├── api/            # Endpoints REST
│   │   ├── core/           # Config, Security
│   │   ├── models/         # SQLAlchemy models
│   │   ├── services/       # Lógica de negocio
│   │   └── tools/          # LangChain Tools
│   └── alembic/            # Migraciones DB
├── frontend/               # UI Streamlit
├── docs/                   # Documentación
└── docker-compose.yml      # Orquestación
```

---

## 🛠️ Stack Tecnológico

| Categoría | Tecnología |
|-----------|------------|
| **Backend** | FastAPI 0.109, Python 3.11 |
| **Frontend** | Streamlit 1.31 |
| **IA** | LangChain 0.1.0, LangGraph 0.0.20, Google Gemini |
| **Base de Datos** | PostgreSQL 15 + pgvector |
| **Cache** | Redis 7 |
| **Contenedores** | Docker, Docker Compose |
| **Auth** | JWT (PyJWT) + bcrypt |

---

## � Deploy a Producción (Cloud Run)

```bash
# Deploy rápido con script
./deploy.sh all

# O con GitHub Actions (push a main)
git push origin main
```

📖 **[Guía completa de deploy →](docs/DEPLOY.md)**

### Costos: $0/mes (Free Tier)
- Google Cloud Run: 2M requests gratis
- Supabase PostgreSQL: 500MB gratis
- Upstash Redis: 10K commands/día gratis
- Gemini API: 1M tokens/día gratis

---

## 🧪 Testing

```bash
# Ejecutar todos los tests
docker compose exec backend pytest tests/ -v

# Con coverage
docker compose exec backend pytest tests/ --cov=app --cov-report=html
```

**Estado actual:** 37 tests passing ✅

---

## 📖 Documentación

- 📚 [Guía Rápida de Inicio](docs/QUICK_START.md)
- 🚀 [Deploy a Cloud Run](docs/DEPLOY.md)
- 📊 [Progreso del Proyecto](docs/PROJECT_PROGRESS.md)
- 📋 [Instrucciones para Copilot](.github/copilot-instructions.md)

---

## 👥 Equipo

| Nombre | Rol |
|--------|-----|
| David Emmanuel Jauregui | Desarrollador |
| Oscar Ruiz | Desarrollador |
| Gustavo Iván Meraz | Desarrollador |

**Universidad del Caribe** - Proyecto Terminal 2024

---

## 📄 Licencia

Este proyecto es parte de un trabajo académico de la Universidad del Caribe.

---

*Última actualización: Enero 2026*
