# Models package
from app.models.universidad import Universidad
from app.models.carrera import Carrera
from app.models.estudiante import Estudiante
from app.models.sesion_consultoria import SesionConsultoria
from app.models.universidad_info import UniversidadInfo

__all__ = [
    "Universidad",
    "Carrera",
    "Estudiante",
    "SesionConsultoria",
    "UniversidadInfo"
]