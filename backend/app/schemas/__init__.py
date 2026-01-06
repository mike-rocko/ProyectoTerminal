# Schemas module - Pydantic schemas para request/response
from app.schemas.universidad import UniversidadCreate, UniversidadUpdate, UniversidadResponse
from app.schemas.carrera import CarreraCreate, CarreraUpdate, CarreraResponse
from app.schemas.estudiante import EstudianteCreate, EstudianteUpdate, EstudianteResponse
from app.schemas.auth import Token, TokenData, LoginRequest, RegisterRequest

__all__ = [
    "UniversidadCreate", "UniversidadUpdate", "UniversidadResponse",
    "CarreraCreate", "CarreraUpdate", "CarreraResponse",
    "EstudianteCreate", "EstudianteUpdate", "EstudianteResponse",
    "Token", "TokenData", "LoginRequest", "RegisterRequest"
]
