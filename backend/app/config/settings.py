"""
Configuración central del proyecto usando Pydantic Settings.
Todas las variables de entorno se cargan desde .env
"""
from pydantic_settings import BaseSettings
from typing import Optional


class Settings(BaseSettings):
    """Configuración de la aplicación"""
    
    # Información del Proyecto
    project_name: str = "Tutor IA - Sistema Multi-Universidad"
    version: str = "0.1.0"
    api_prefix: str = "/api/v1"
    
    # Base de Datos PostgreSQL
    database_url: str
    db_echo: bool = False  # True para ver queries SQL
    
    # Redis Cache
    redis_url: str = "redis://localhost:6379"
    redis_password: Optional[str] = None
    
    # Google AI (Gemini)
    google_api_key: str
    gemini_model: str = "gemini-1.5-pro"
    gemini_flash_model: str = "gemini-1.5-flash"
    gemini_embedding_model: str = "models/embedding-001"
    
    # Google Cloud Storage (para imágenes)
    gcs_bucket_name: Optional[str] = None
    gcs_credentials_path: Optional[str] = None
    
    # Autenticación JWT
    secret_key: str
    algorithm: str = "HS256"
    access_token_expire_minutes: int = 60 * 24 * 7  # 7 días
    
    # LangSmith (Observabilidad - Opcional)
    langsmith_api_key: Optional[str] = None
    langsmith_project: Optional[str] = "tutor-ia"
    langchain_tracing_v2: bool = False
    
    # CORS
    backend_cors_origins: list = ["http://localhost:3000", "http://localhost:8000"]
    
    # Archivos
    max_upload_size_mb: int = 10
    allowed_file_types: list = [".jpg", ".jpeg", ".png", ".pdf", ".xlsx", ".xls", ".docx"]
    uploads_dir: str = "uploads"
    
    # Multi-tenancy
    default_timezone: str = "America/Cancun"  # UniCaribe
    
    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"
        case_sensitive = False


# Instancia global de settings
settings = Settings()
