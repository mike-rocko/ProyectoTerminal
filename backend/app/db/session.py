"""
Base de datos - Configuración de SQLAlchemy
"""
from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from app.config.settings import settings

# Engine de SQLAlchemy
engine = create_engine(
    settings.database_url,
    echo=settings.db_echo,  # Ver queries SQL en desarrollo
    pool_pre_ping=True,  # Verificar conexión antes de usar
    pool_size=5,
    max_overflow=10
)

# SessionLocal para crear sesiones de DB
SessionLocal = sessionmaker(
    autocommit=False,
    autoflush=False,
    bind=engine
)

# Base declarativa para los modelos
Base = declarative_base()


def get_db():
    """
    Dependency para FastAPI.
    Crea una sesión de DB y la cierra al terminar.
    
    Uso:
        @app.get("/items")
        def get_items(db: Session = Depends(get_db)):
            ...
    """
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
