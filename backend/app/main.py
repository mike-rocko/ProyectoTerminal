from fastapi import FastAPI, Depends
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session
from app.config.settings import settings
from app.config.dependencies import get_db
from app.models.universidad import Universidad
# from app.tools.dummy_tool import DummyTool  # Comentado temporalmente

app = FastAPI(
    title=settings.project_name,
    description="API del Sistema Multi-Universidad de Tutoría Inteligente",
    version=settings.version
)

# CORS Middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.backend_cors_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/")
async def root():
    return {
        "message": settings.project_name,
        "version": settings.version,
        "status": "running",
        "docs": "/docs"
    }

@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {
        "status": "healthy",
        "project": settings.project_name,
        "version": settings.version
        # TODO: Agregar checks de DB y Redis
    }

@app.get("/test-db")
async def test_database(db: Session = Depends(get_db)):
    """Test database connection y crear universidad de prueba"""
    try:
        # Verificar si ya existe UniCaribe
        universidad = db.query(Universidad).filter(Universidad.slug == "unicaribe").first()
        
        if not universidad:
            # Crear universidad de prueba
            universidad = Universidad(
                nombre="Universidad del Caribe",
                slug="unicaribe",
                email_contacto="contacto@unicaribe.mx",
                telefono="998-881-4400",
                direccion="SM 78, Mza 1, Lote 1, Cancún, Q. Roo",
                sitio_web="https://www.unicaribe.mx",
                config={
                    "timezone": "America/Cancun",
                    "idioma_default": "es"
                },
                colores_tema={
                    "primary": "#003366",
                    "secondary": "#FF6600"
                }
            )
            db.add(universidad)
            db.commit()
            db.refresh(universidad)
            
            return {
                "status": "success",
                "message": "Universidad creada exitosamente",
                "universidad": {
                    "id": str(universidad.id),
                    "nombre": universidad.nombre,
                    "slug": universidad.slug
                }
            }
        else:
            return {
                "status": "success",
                "message": "Universidad ya existe",
                "universidad": {
                    "id": str(universidad.id),
                    "nombre": universidad.nombre,
                    "slug": universidad.slug
                }
            }
    except Exception as e:
        return {
            "status": "error",
            "message": f"Error de conexión a BD: {str(e)}"
        }

# TODO: Importar y registrar routers
# from app.api import auth, estudiantes, consultoria, universidades
# app.include_router(auth.router, prefix=f"{settings.api_prefix}/auth", tags=["auth"])
# app.include_router(estudiantes.router, prefix=f"{settings.api_prefix}/estudiantes", tags=["estudiantes"])
