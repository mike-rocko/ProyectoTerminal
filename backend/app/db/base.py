"""
Base declarativa para todos los modelos.
Importar todos los modelos aquí para que Alembic los detecte.
"""
from app.db.session import Base

# Importar TODOS los modelos aquí (para Alembic)
from app.models.universidad import Universidad
from app.models.carrera import Carrera
from app.models.estudiante import Estudiante
from app.models.sesion_consultoria import SesionConsultoria
from app.models.universidad_info import UniversidadInfo

# Esta lista ayuda a Alembic a detectar todos los modelos
__all__ = [
    "Base",
    "Universidad",
    "Carrera",
    "Estudiante",
    "SesionConsultoria",
    "UniversidadInfo"
]
