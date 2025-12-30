# 🚀 GUÍA DE SETUP RÁPIDO - TUTOR IA

## ✅ LO QUE YA ESTÁ HECHO:
- ✅ Estructura de carpetas
- ✅ 5 modelos SQLAlchemy profesionales creados
- ✅ Alembic inicializado
- ✅ Dependencies instaladas
- ✅ SECRET_KEY generado

---

## 📋 COMPLETAR CONFIGURACIÓN (5 minutos)

### PASO 1: Obtener Google AI API Key (GRATIS)

1. Abrir: https://makersuite.google.com/app/apikey
2. Click en "Create API Key"
3. Copiar la key que empieza con `AIzaSy...`

### PASO 2: Configurar Supabase (GRATIS)

1. Abrir: https://supabase.com/dashboard
2. Crear cuenta (GitHub login recomendado)
3. Click "New Project"
   - Name: `tutor-ia-dev`
   - Database Password: [ANOTAR ESTO]
   - Region: `South America (São Paulo)` (más cercano)
4. Esperar 2 minutos a que se cree
5. Ir a `Settings > Database`
6. Copiar la **Connection String (URI)**
   - Se ve así: `postgresql://postgres.[xxx]:[YOUR-PASSWORD]@aws-0-sa-east-1.pooler.supabase.com:5432/postgres`
   - ⚠️ IMPORTANTE: Reemplazar `[YOUR-PASSWORD]` con tu password del paso 3

### PASO 3: Editar archivo .env

Abrir: `backend/.env` y completar:

```env
# Google AI (del Paso 1)
GOOGLE_API_KEY=AIzaSy...TU_KEY_AQUI

# Supabase (del Paso 2)
DATABASE_URL=postgresql://postgres.[xxx]:TU_PASSWORD@aws-0-sa-east-1.pooler.supabase.com:5432/postgres

# Secret Key (ya generado)
SECRET_KEY=218d8050090c055ac06c3c5abef9e05d3e854f14b229ce73c898b9a10a423ad9
```

### PASO 4: Habilitar pgvector en Supabase

1. En Supabase Dashboard, ir a `SQL Editor`
2. Pegar este comando:
```sql
CREATE EXTENSION IF NOT EXISTS vector;
```
3. Click "Run"
4. Debería decir: "Success. No rows returned"

---

## 🚀 CREAR BASE DE DATOS

Una vez completado el .env:

```powershell
# 1. Crear primera migración (crea las tablas)
alembic revision --autogenerate -m "initial tables"

# 2. Aplicar migración
alembic upgrade head

# 3. Verificar que funcionó
alembic current
```

---

## ▶️ EJECUTAR SERVIDOR

```powershell
uvicorn app.main:app --reload
```

Abrir: http://localhost:8000/docs

---

## ✨ LO QUE TENDRÁS PARA TU CV:

✅ **PostgreSQL con pgvector** (Base de datos vectorial)
✅ **Arquitectura Multi-tenant** (Escalable)
✅ **Alembic Migrations** (Profesional)
✅ **5 Modelos Relacionales** (ORM avanzado)
✅ **Embeddings para RAG** (IA moderna)
✅ **Google Gemini integrado** (LLM de punta)

---

## 🆘 SI ALGO FALLA:

**Error: "ModuleNotFoundError: No module named 'app'"**
```powershell
# Asegúrate de estar en backend/
cd backend
```

**Error: "Connection refused"**
- Verificar que DATABASE_URL en .env sea correcto
- Verificar password de Supabase

**Error: "Invalid API key"**
- Verificar GOOGLE_API_KEY en .env

---

**SIGUIENTE:** Una vez que funcione, continuamos con el Vision Tool 🎯
