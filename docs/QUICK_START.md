# 🚀 Inicio Rápido - Tutor IA

> **Tiempo estimado:** 2 minutos

---

## 📋 Requisitos

- **Docker** 24.0+ (`docker --version`)
- **Docker Compose** 2.20+ (`docker compose version`)

---

## ⚡ Comandos Rápidos

### Opción 1: Todo en un comando
```bash
# Clonar, configurar y levantar
git clone https://github.com/tu-usuario/ProyectoTerminal.git && cd ProyectoTerminal && cp backend/.env.example backend/.env && docker compose up -d --build
```

### Opción 2: Paso a paso

```bash
# 1. Clonar
git clone https://github.com/tu-usuario/ProyectoTerminal.git
cd ProyectoTerminal

# 2. Configurar (opcional: editar backend/.env y agregar GOOGLE_API_KEY)
cp backend/.env.example backend/.env

# 3. Levantar
docker compose up -d --build

# 4. Migraciones (primera vez)
docker compose exec backend alembic upgrade head
```

---

## 🌐 URLs

| Servicio | URL | Descripción |
|----------|-----|-------------|
| **🎓 Portal Estudiantes** | http://localhost:8501 | Chat y horarios |
| **🏛️ Panel Admin** | http://localhost:8502 | Gestión universidad |
| **📖 API Docs** | http://localhost:8000/docs | Swagger UI |
| **❤️ Health Check** | http://localhost:8000/health | Estado del sistema |

---

## 🔑 Credenciales de Prueba

### Admin Universidad
```
Email: admin@unicaribe.edu.mx
Pass:  Admin123!
```

### Estudiante
```
Email: gustavo@unicaribe.edu.mx
Pass:  Test123!
```

---

## 🛠️ Comandos Útiles

```bash
# Ver logs en tiempo real
docker compose logs -f

# Ver logs de un servicio específico
docker compose logs -f backend

# Reiniciar un servicio
docker compose restart backend

# Reconstruir después de cambios
docker compose up -d --build

# Parar todo
docker compose down

# Parar y eliminar volúmenes (BORRA DATOS)
docker compose down -v

# Entrar al contenedor del backend
docker compose exec backend bash

# Limpiar cache de Redis
docker compose exec redis redis-cli FLUSHALL
```

---

## 🔧 Troubleshooting

### El backend no inicia
```bash
docker compose logs backend
docker compose restart backend
```

### Error de migraciones
```bash
docker compose down -v
docker compose up -d
docker compose exec backend alembic upgrade head
```

### Limpiar todo y empezar de cero
```bash
docker compose down -v --rmi all
docker compose up -d --build
docker compose exec backend alembic upgrade head
```

---

## ✅ Verificar que todo funciona

```bash
curl http://localhost:8000/health
# Debería mostrar: {"status":"healthy","database":"connected","redis":"connected"}
```

---

**¿Problemas?** Abre un issue en GitHub.
