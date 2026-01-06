from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy import text
import redis.asyncio as redis

from app.core.config import settings
from app.db.session import AsyncSessionLocal
from app.tools.dummy_tool import DummyTool
from app.api.auth import router as auth_router
from app.api.vision import router as vision_router
from app.api.schedule import router as schedule_router
from app.api.rag import router as rag_router
from app.api.agent import router as agent_router
from app.api.admin import router as admin_router

app = FastAPI(
    title="Tutor IA API",
    description="API del Agente Inteligente de Acompañamiento Académico",
    version="0.1.0"
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Registrar routers
app.include_router(auth_router, prefix="/api/v1")
app.include_router(vision_router, prefix="/api/v1")
app.include_router(schedule_router, prefix="/api/v1")
app.include_router(rag_router, prefix="/api/v1")
app.include_router(agent_router, prefix="/api/v1")
app.include_router(admin_router)  # Ya tiene prefix /api/v1/admin

@app.get("/")
async def root():
    return {
        "message": "Tutor IA API",
        "version": "0.1.0",
        "status": "running"
    }

@app.get("/health")
async def health_check():
    """
    Verifica conexión real a PostgreSQL y Redis.
    """
    health = {
        "status": "healthy",
        "database": "disconnected",
        "redis": "disconnected"
    }
    
    # Verificar PostgreSQL
    try:
        async with AsyncSessionLocal() as session:
            await session.execute(text("SELECT 1"))
            health["database"] = "connected"
    except Exception as e:
        health["status"] = "unhealthy"
        health["database_error"] = str(e)
    
    # Verificar Redis
    try:
        redis_client = redis.from_url(settings.redis_url)
        await redis_client.ping()
        await redis_client.close()
        health["redis"] = "connected"
    except Exception as e:
        health["status"] = "unhealthy"
        health["redis_error"] = str(e)
    
    return health

# NUEVO: Endpoint para probar la herramienta
@app.get("/test-tool/{student_id}")
async def test_tool(student_id: str):
    tool = DummyTool()
    result = tool._run(student_id)
    return {
        "student_id": student_id,
        "result": result
    }