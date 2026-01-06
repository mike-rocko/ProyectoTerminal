"""
Configuración de sesión de base de datos con SQLAlchemy.
Soporta tanto sync como async.
"""
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, Session
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession, async_sessionmaker

from app.core.config import settings


# ============================================
# Motor Sincrónico (para Alembic y scripts)
# ============================================
engine = create_engine(
    settings.database_url,
    pool_pre_ping=True,  # Verifica conexión antes de usar
    pool_size=5,
    max_overflow=10,
    echo=not settings.is_production  # Log SQL en desarrollo
)

SessionLocal = sessionmaker(
    autocommit=False,
    autoflush=False,
    bind=engine
)


# ============================================
# Motor Asincrónico (para FastAPI)
# ============================================
async_engine = create_async_engine(
    settings.database_url_async,
    pool_pre_ping=True,
    pool_size=5,
    max_overflow=10,
    echo=not settings.is_production
)

AsyncSessionLocal = async_sessionmaker(
    bind=async_engine,
    class_=AsyncSession,
    autocommit=False,
    autoflush=False,
    expire_on_commit=False
)


# ============================================
# Dependency Injection para FastAPI
# ============================================
async def get_db() -> AsyncSession:
    """
    Dependency que provee una sesión de base de datos.
    
    Uso en endpoints:
        @app.get("/ejemplo")
        async def ejemplo(db: AsyncSession = Depends(get_db)):
            ...
    """
    async with AsyncSessionLocal() as session:
        try:
            yield session
            await session.commit()
        except Exception:
            await session.rollback()
            raise
        finally:
            await session.close()


def get_db_sync() -> Session:
    """
    Versión sincrónica para scripts y Alembic.
    """
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
