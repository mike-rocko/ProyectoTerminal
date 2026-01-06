"""
Configuración central de la aplicación.
Usa Pydantic Settings para cargar variables de entorno.
"""
from typing import Optional
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """
    Configuración de la aplicación cargada desde variables de entorno.
    
    Las variables se cargan automáticamente desde:
    1. Variables de entorno del sistema
    2. Archivo .env (si existe)
    """
    
    # Entorno
    environment: str = "development"
    
    # Base de datos
    database_url: str = "postgresql://postgres:postgres_dev@postgres:5432/tutor_ia"
    
    # Redis
    redis_url: str = "redis://redis:6379"
    
    # Google AI (Gemini)
    google_api_key: Optional[str] = None
    
    # JWT
    jwt_secret_key: str = "dev-secret-key-change-in-production"
    jwt_algorithm: str = "HS256"
    access_token_expire_minutes: int = 1440  # 24 horas
    
    # LangSmith
    langchain_tracing_v2: bool = False
    langchain_api_key: Optional[str] = None
    langchain_project: str = "tutor-ia"
    
    # Configuración del modelo
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
        extra="ignore"
    )
    
    @property
    def is_production(self) -> bool:
        """Retorna True si estamos en producción."""
        return self.environment == "production"
    
    @property
    def database_url_async(self) -> str:
        """Retorna URL de base de datos para asyncpg."""
        return self.database_url.replace("postgresql://", "postgresql+asyncpg://")


# Instancia global de settings
settings = Settings()
