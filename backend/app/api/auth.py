"""
Endpoints de autenticación.
"""
from fastapi import APIRouter, Depends, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.session import get_db
from app.core.dependencies import get_current_user
from app.models.estudiante import Estudiante
from app.schemas.auth import RegisterRequest, LoginRequest, AuthResponse
from app.schemas.estudiante import EstudianteResponse
from app.services.auth_service import AuthService


router = APIRouter(prefix="/auth", tags=["Autenticación"])


@router.post(
    "/register",
    response_model=AuthResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Registrar nuevo estudiante",
    description="""
    Registra un nuevo estudiante en el sistema.
    
    Requiere:
    - universidad_slug: Identificador de la universidad (ej: "unicaribe")
    - matricula: Matrícula del estudiante
    - email: Email institucional
    - password: Contraseña (mínimo 8 caracteres)
    
    Retorna token JWT para autenticación.
    """
)
async def register(
    data: RegisterRequest,
    db: AsyncSession = Depends(get_db)
):
    """Registra un nuevo estudiante y retorna token de acceso."""
    service = AuthService(db)
    return await service.register(data)


@router.post(
    "/login",
    response_model=AuthResponse,
    summary="Iniciar sesión",
    description="""
    Autentica un estudiante con email y contraseña.
    
    Retorna token JWT válido por 24 horas.
    """
)
async def login(
    data: LoginRequest,
    db: AsyncSession = Depends(get_db)
):
    """Autentica estudiante y retorna token de acceso."""
    service = AuthService(db)
    return await service.login(data)


@router.get(
    "/me",
    response_model=EstudianteResponse,
    summary="Obtener usuario actual",
    description="""
    Retorna información del estudiante autenticado.
    
    Requiere token JWT en header: `Authorization: Bearer <token>`
    """
)
async def get_me(
    user: Estudiante = Depends(get_current_user)
):
    """Retorna datos del usuario autenticado."""
    return EstudianteResponse.model_validate(user)


@router.post(
    "/refresh",
    response_model=AuthResponse,
    summary="Refrescar token",
    description="Genera un nuevo token JWT usando el token actual."
)
async def refresh_token(
    user: Estudiante = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Genera nuevo token para el usuario autenticado."""
    from app.schemas.auth import Token
    from app.core.security import create_access_token
    from app.core.config import settings
    
    access_token = create_access_token(
        estudiante_id=user.id,
        universidad_id=user.universidad_id,
        email=user.email
    )
    
    token = Token(
        access_token=access_token,
        token_type="bearer",
        expires_in=settings.access_token_expire_minutes * 60
    )
    
    return AuthResponse(
        token=token,
        user=EstudianteResponse.model_validate(user).model_dump()
    )
