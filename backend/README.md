# 🎓 Tutor IA - Sistema Multi-Universidad

Sistema de tutoría inteligente que ayuda a estudiantes universitarios a armar horarios optimizados y consultar información de su universidad mediante IA.

## 🚀 Stack Tecnológico

- **Backend:** FastAPI + Python 3.11
- **Base de Datos:** PostgreSQL 15 + pgvector
- **IA:** Google Gemini 1.5 Pro + LangChain + LangGraph
- **Cache:** Redis
- **Algoritmos:** NetworkX (grafos de prerrequisitos)

## 📋 Prerequisitos

1. **Python 3.11+**
2. **PostgreSQL 15+** (recomendado: [Supabase](https://supabase.com) - gratis)
3. **Redis** (opcional para MVP)
4. **Google AI API Key** ([obtener aquí](https://makersuite.google.com/app/apikey))

## ⚙️ Setup Local (Primeros Pasos)

### 1. Clonar el repositorio
```bash
git clone <repo-url>
cd ProyectoTerminal/backend
```

### 2. Crear entorno virtual
```bash
python -m venv venv

# Activar (Windows)
venv\Scripts\activate

# Activar (Mac/Linux)
source venv/bin/activate
```

### 3. Instalar dependencias
```bash
pip install -r requirements.txt
```

### 4. Configurar variables de entorno
```bash
# Copiar el ejemplo
cp .env.example .env

# Editar .env y completar:
# - DATABASE_URL
# - GOOGLE_API_KEY
# - SECRET_KEY (generar uno: python -c "import secrets; print(secrets.token_hex(32))")
```

#### Opción A: PostgreSQL con Supabase (Recomendado)
1. Ir a [supabase.com](https://supabase.com)
2. Crear proyecto gratis
3. En `Settings > Database`, copiar la Connection String
4. Pegar en `DATABASE_URL` en `.env`

#### Opción B: PostgreSQL Local
```bash
# Instalar PostgreSQL
# Windows: https://www.postgresql.org/download/windows/
# Mac: brew install postgresql

# Crear base de datos
createdb tutor_ia_dev

# En .env:
DATABASE_URL=postgresql://postgres:tu_password@localhost:5432/tutor_ia_dev
```

### 5. Inicializar base de datos
```bash
# Crear tablas (cuando estén los modelos)
alembic upgrade head
```

### 6. Ejecutar servidor
```bash
uvicorn app.main:app --reload
```

Abrir: http://localhost:8000/docs (Swagger UI)

## 📁 Estructura del Proyecto

```
backend/
├── app/
│   ├── agents/         # LangGraph agents
│   ├── api/            # FastAPI endpoints
│   ├── config/         # Settings & dependencies
│   ├── core/           # Algoritmos (validators, schedule builder)
│   ├── db/             # Database session
│   ├── models/         # SQLAlchemy models
│   ├── schemas/        # Pydantic schemas
│   ├── services/       # Business logic
│   └── tools/          # LangChain tools
├── tests/              # Tests
├── alembic/            # Database migrations
├── .env                # Variables de entorno (NO en Git)
├── requirements.txt
└── README.md
```

## 🧪 Tests

```bash
pytest
```

## 🐳 Docker (Opcional)

```bash
docker-compose up -d
```

## 📝 Próximos Pasos

- [ ] Crear modelos SQLAlchemy
- [ ] Implementar Vision Tool (Gemini)
- [ ] Construir algoritmo de validación de prerrequisitos
- [ ] Desarrollar Schedule Builder
- [ ] Implementar RAG para info universidad

## 👥 Equipo

- David Emmanuel Jauregui
- Oscar Ruiz
- Gustavo Iván Meraz

**Universidad del Caribe - Semestre Terminal 2024**

---

## 🆘 Troubleshooting

### Error: "ModuleNotFoundError"
```bash
pip install -r requirements.txt
```

### Error: "Could not connect to database"
Verificar que PostgreSQL esté corriendo y que `DATABASE_URL` en `.env` sea correcto.

### Error: "Invalid API Key"
Verificar que `GOOGLE_API_KEY` en `.env` sea válido.

## 📚 Documentación

- [Arquitectura](../docs/arquitectura.md)
- [API Docs](http://localhost:8000/docs)
- [Copilot Instructions](../.github/copilot-instructions.md)
