from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.tools.dummy_tool import DummyTool  # NUEVO

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

@app.get("/")
async def root():
    return {
        "message": "Tutor IA API",
        "version": "0.1.0",
        "status": "running"
    }

@app.get("/health")
async def health_check():
    return {
        "status": "healthy",
        "database": "connected",
        "redis": "connected"
    }

# NUEVO: Endpoint para probar la herramienta
@app.get("/test-tool/{student_id}")
async def test_tool(student_id: str):
    tool = DummyTool()
    result = tool._run(student_id)
    return {
        "student_id": student_id,
        "result": result
    }