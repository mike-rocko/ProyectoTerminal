# 🚀 Guía Rápida de Inicio - Tutor IA

> Guía paso a paso para correr el proyecto después de clonarlo desde GitHub.

---

## 📋 Requisitos Previos

### Software Necesario
| Software | Versión Mínima | Verificar Instalación |
|----------|---------------|----------------------|
| **Docker** | 24.0+ | `docker --version` |
| **Docker Compose** | 2.20+ | `docker compose version` |
| **Git** | 2.30+ | `git --version` |

### APIs Requeridas (Gratuitas)
- **Google AI API Key** - Para Gemini Vision y Chat
  - Obtener en: https://aistudio.google.com/app/apikey

---

## 🏃 Inicio Rápido (5 minutos)

### 1️⃣ Clonar el Repositorio
```bash
git clone https://github.com/tu-usuario/ProyectoTerminal.git
cd ProyectoTerminal
```

### 2️⃣ Configurar Variables de Entorno
```bash
# Crear archivo .env para el backend
cp backend/.env.example backend/.env

# Editar y agregar tu API key de Google
nano backend/.env
```

**Contenido mínimo de `backend/.env`:**
```env
# API de Google AI (REQUERIDO)
GOOGLE_API_KEY=tu_api_key_aqui

# Base de datos (no cambiar si usas Docker)
DATABASE_URL=postgresql://postgres:postgres_dev@postgres:5432/tutor_ia
ASYNC_DATABASE_URL=postgresql+asyncpg://postgres:postgres_dev@postgres:5432/tutor_ia

# Redis
REDIS_URL=redis://redis:6379

# JWT (puedes dejar estos valores para desarrollo)
SECRET_KEY=dev_secret_key_change_in_production
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=30

# Entorno
ENVIRONMENT=development
```

### 3️⃣ Levantar los Servicios
```bash
# Construir e iniciar todos los contenedores
docker compose up -d --build

# Verificar que todos estén corriendo
docker compose ps
```

**Salida esperada:**
```
NAME                          STATUS          PORTS
proyectoterminal-postgres-1   Up              0.0.0.0:5432->5432/tcp
proyectoterminal-redis-1      Up              0.0.0.0:6379->6379/tcp
proyectoterminal-backend-1    Up              0.0.0.0:8000->8000/tcp
proyectoterminal-frontend-1   Up (healthy)    0.0.0.0:8501->8501/tcp
```

### 4️⃣ Ejecutar Migraciones de Base de Datos
```bash
docker compose exec backend alembic upgrade head
```

### 5️⃣ ¡Listo! Abrir la Aplicación

| Servicio | URL | Descripción |
|----------|-----|-------------|
| **Frontend** | http://localhost:8501 | Interfaz Streamlit |
| **API Docs** | http://localhost:8000/docs | Documentación Swagger |
| **API Health** | http://localhost:8000/health | Estado del sistema |

---

## 🧪 Verificar que Todo Funciona

### Test 1: Backend Health Check
```bash
curl http://localhost:8000/health
```
**Respuesta esperada:**
```json
{"status": "healthy", "database": "connected", "redis": "connected"}
```

### Test 2: Chat con el Agente
```bash
curl -X POST http://localhost:8000/api/v1/agent/chat \
  -H "Content-Type: application/json" \
  -d '{
    "universidad_id": "11111111-1111-1111-1111-111111111111",
    "message": "Hola, quiero armar mi horario"
  }'
```

### Test 3: Generar Horarios de Prueba
```bash
curl -X POST http://localhost:8000/api/v1/schedule/generate-test
```

### Test 4: Probar RAG (primero cargar datos)
```bash
# Cargar datos de ejemplo
curl -X POST http://localhost:8000/api/v1/rag/ingest-test

# Hacer una pregunta
curl -X POST http://localhost:8000/api/v1/rag/ask \
  -H "Content-Type: application/json" \
  -d '{
    "query": "¿Cuántas materias puedo inscribir?",
    "universidad_id": "11111111-1111-1111-1111-111111111111"
  }'
```

---

## 📁 Estructura del Proyecto

```
ProyectoTerminal/
├── backend/                 # API FastAPI
│   ├── app/
│   │   ├── agents/         # Agente LangGraph
│   │   ├── api/            # Endpoints REST
│   │   ├── core/           # Config, Security
│   │   ├── db/             # Database session
│   │   ├── models/         # SQLAlchemy models
│   │   ├── schemas/        # Pydantic schemas
│   │   ├── services/       # Lógica de negocio
│   │   └── tools/          # LangChain Tools
│   ├── alembic/            # Migraciones DB
│   ├── Dockerfile
│   └── requirements.txt
├── frontend/               # UI Streamlit
│   ├── app.py             # Aplicación principal
│   ├── api_client.py      # Cliente HTTP
│   ├── config.py          # Configuración
│   ├── Dockerfile
│   └── requirements.txt
├── docs/                   # Documentación
├── uploads/                # Archivos subidos
├── docker-compose.yml      # Orquestación
└── README.md
```

---

## 🔧 Comandos Útiles

### Gestión de Contenedores
```bash
# Ver estado de servicios
docker compose ps

# Ver logs en tiempo real
docker compose logs -f

# Ver logs de un servicio específico
docker compose logs backend -f
docker compose logs frontend -f

# Reiniciar un servicio
docker compose restart backend

# Parar todo
docker compose down

# Parar y eliminar volúmenes (CUIDADO: borra datos)
docker compose down -v
```

### Desarrollo
```bash
# Reconstruir después de cambios en requirements.txt
docker compose build backend
docker compose build frontend

# Entrar al contenedor del backend
docker compose exec backend bash

# Ejecutar migraciones
docker compose exec backend alembic upgrade head

# Crear nueva migración
docker compose exec backend alembic revision --autogenerate -m "descripcion"
```

### Base de Datos
```bash
# Conectar a PostgreSQL
docker compose exec postgres psql -U postgres -d tutor_ia

# Ver tablas
\dt

# Ver datos de una tabla
SELECT * FROM estudiantes;

# Salir
\q
```

---

## ⚠️ Solución de Problemas

### Error: "Connection refused" al acceder a localhost:8000
```bash
# Verificar que el backend está corriendo
docker compose logs backend

# Si hay error de migraciones, ejecutar:
docker compose exec backend alembic upgrade head
```

### Error: "API key not valid"
- Verifica que `GOOGLE_API_KEY` esté correctamente configurado en `backend/.env`
- Asegúrate de que la API key sea válida en https://aistudio.google.com/

### Error: "Rate limit exceeded" en Gemini
- Estás haciendo muchas llamadas muy rápido
- Espera unos minutos antes de continuar
- El free tier tiene límites de 15 req/min para Flash

### Frontend no conecta con Backend
```bash
# Verificar que el backend responde
curl http://localhost:8000/health

# Ver logs del frontend para errores de conexión
docker compose logs frontend
```

### Base de datos no tiene tablas
```bash
# Ejecutar migraciones
docker compose exec backend alembic upgrade head
```

### Resetear todo desde cero
```bash
# Parar y eliminar volúmenes
docker compose down -v

# Reconstruir todo
docker compose up -d --build

# Ejecutar migraciones
docker compose exec backend alembic upgrade head
```

---

## 🎯 Uso Básico de la Aplicación

### 1. Acceder al Frontend
- Abre http://localhost:8501
- Usa el botón **"🚀 Modo Demo"** para entrar sin registro

### 2. Chatear con el Agente
- Escribe mensajes como "Hola" o "Quiero armar mi horario"
- El agente detectará tu intención y responderá

### 3. Subir Documentos
- Ve a la sección **"📄 Documentos"**
- Sube tu Kárdex (imagen o PDF)
- Sube la Oferta Académica
- Haz clic en "🔍 Analizar"

### 4. Ver Horarios Generados
- Ve a **"📅 Horarios"**
- Haz clic en "🧪 Generar Horario de Prueba"
- Explora las opciones rankeadas

### 5. Preguntar sobre la Universidad
- Ve a **"ℹ️ Info Universidad"**
- Escribe preguntas como "¿Cuándo son las inscripciones?"

---

## 📞 Soporte

**Equipo de Desarrollo:**
- David Emmanuel Jauregui
- Oscar Ruiz
- Gustavo Iván Meraz

**Universidad del Caribe** - Proyecto Terminal 2024

---

*Última actualización: 6 de Enero 2026*
