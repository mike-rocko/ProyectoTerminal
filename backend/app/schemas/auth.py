"""
Schemas para Autenticación.
"""
from typing import Optional
from uuid import UUID

from pydantic import BaseModel, Field, EmailStr


# ============================================
# Request Schemas
# ============================================

class LoginRequest(BaseModel):
    """Schema para login."""
    email: EmailStr
    password: str = Field(..., min_length=1)


class RegisterRequest(BaseModel):
    """Schema para registro de estudiante."""
    # El slug de la universidad viene en la URL o header
    universidad_slug: str = Field(..., min_length=3, max_length=100)
    matricula: str = Field(..., min_length=5, max_length=50, examples=["20-1234"])
    email: EmailStr = Field(..., examples=["estudiante@unicaribe.edu.mx"])
    password: str = Field(..., min_length=8)
    nombre: Optional[str] = Field(None, max_length=100)
    apellido: Optional[str] = Field(None, max_length=100)
    carrera_id: Optional[UUID] = None


class PasswordChangeRequest(BaseModel):
    """Schema para cambio de contraseña."""
    current_password: str
    new_password: str = Field(..., min_length=8)


# ============================================
# Response Schemas
# ============================================

class Token(BaseModel):
    """Schema de respuesta para token JWT."""
    access_token: str
    token_type: str = "bearer"
    expires_in: int  # Segundos hasta expiración


class TokenData(BaseModel):
    """Datos decodificados del token."""
    sub: str  # estudiante_id
    universidad_id: UUID
    email: str
    exp: int


class AuthResponse(BaseModel):
    """Respuesta completa de autenticación."""
    token: Token
    user: dict  # EstudianteResponse serializado
