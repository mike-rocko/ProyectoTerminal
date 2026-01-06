# Models module - Modelos SQLAlchemy
from app.models.universidad import Universidad
from app.models.carrera import Carrera
from app.models.estudiante import Estudiante
from app.models.sesion import SesionConsultoria
from app.models.universidad_info import UniversidadInfo
from app.models.admin_universidad import AdminUniversidad

__all__ = [
    "Universidad", 
    "Carrera", 
    "Estudiante", 
    "SesionConsultoria", 
    "UniversidadInfo",
    "AdminUniversidad"
]
