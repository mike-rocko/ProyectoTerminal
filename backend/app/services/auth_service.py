"""
Servicio de autenticación.
Lógica de negocio para registro, login y manejo de usuarios.
"""
from typing import Optional
from uuid import UUID

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from fastapi import HTTPException, status

from app.models.estudiante import Estudiante
from app.models.universidad import Universidad
from app.core.security import hash_password, verify_password, create_access_token
from app.schemas.auth import RegisterRequest, LoginRequest, Token, AuthResponse
from app.schemas.estudiante import EstudianteResponse


class AuthService:
    """Servicio para operaciones de autenticación."""
    
    def __init__(self, db: AsyncSession):
        self.db = db
    
    async def register(self, data: RegisterRequest) -> AuthResponse:
        """
        Registra un nuevo estudiante.
        
        Args:
            data: Datos de registro (universidad_slug, matricula, email, password)
            
        Returns:
            AuthResponse con token y datos del usuario
            
        Raises:
            HTTPException 404: Universidad no encontrada
            HTTPException 409: Email o matrícula ya existen
        """
        # 1. Buscar universidad por slug
        universidad = await self._get_universidad_by_slug(data.universidad_slug)
        if universidad is None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Universidad '{data.universidad_slug}' no encontrada"
            )
        
        # 2. Verificar que email no existe
        existing_email = await self._get_estudiante_by_email(data.email)
        if existing_email is not None:
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail="Este email ya está registrado"
            )
        
        # 3. Verificar que matrícula no existe en esta universidad
        existing_matricula = await self._get_estudiante_by_matricula(
            data.matricula, universidad.id
        )
        if existing_matricula is not None:
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail="Esta matrícula ya está registrada en esta universidad"
            )
        
        # 4. Crear estudiante
        estudiante = Estudiante(
            universidad_id=universidad.id,
            matricula=data.matricula,
            email=data.email,
            password_hash=hash_password(data.password),
            nombre=data.nombre,
            apellido=data.apellido,
            carrera_id=data.carrera_id,
            is_active=True,
            is_verified=False  # Pendiente verificación de email
        )
        
        self.db.add(estudiante)
        await self.db.commit()
        await self.db.refresh(estudiante)
        
        # 5. Generar token
        token = self._create_token_response(estudiante)
        
        # 6. Retornar respuesta
        return AuthResponse(
            token=token,
            user=EstudianteResponse.model_validate(estudiante).model_dump()
        )
    
    async def login(self, data: LoginRequest) -> AuthResponse:
        """
        Autentica un estudiante con email y contraseña.
        
        Args:
            data: Credenciales (email, password)
            
        Returns:
            AuthResponse con token y datos del usuario
            
        Raises:
            HTTPException 401: Credenciales inválidas
            HTTPException 403: Usuario desactivado
        """
        # 1. Buscar estudiante por email
        estudiante = await self._get_estudiante_by_email(data.email)
        
        if estudiante is None:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Email o contraseña incorrectos"
            )
        
        # 2. Verificar contraseña
        if not verify_password(data.password, estudiante.password_hash):
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Email o contraseña incorrectos"
            )
        
        # 3. Verificar que está activo
        if not estudiante.is_active:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Tu cuenta ha sido desactivada"
            )
        
        # 4. Generar token
        token = self._create_token_response(estudiante)
        
        # 5. Retornar respuesta
        return AuthResponse(
            token=token,
            user=EstudianteResponse.model_validate(estudiante).model_dump()
        )
    
    def _create_token_response(self, estudiante: Estudiante) -> Token:
        """Crea respuesta de token para un estudiante."""
        from app.core.config import settings
        
        access_token = create_access_token(
            estudiante_id=estudiante.id,
            universidad_id=estudiante.universidad_id,
            email=estudiante.email
        )
        
        return Token(
            access_token=access_token,
            token_type="bearer",
            expires_in=settings.access_token_expire_minutes * 60
        )
    
    async def _get_universidad_by_slug(self, slug: str) -> Optional[Universidad]:
        """Busca universidad por slug."""
        result = await self.db.execute(
            select(Universidad).where(Universidad.slug == slug)
        )
        return result.scalar_one_or_none()
    
    async def _get_estudiante_by_email(self, email: str) -> Optional[Estudiante]:
        """Busca estudiante por email."""
        result = await self.db.execute(
            select(Estudiante).where(Estudiante.email == email)
        )
        return result.scalar_one_or_none()
    
    async def _get_estudiante_by_matricula(
        self, matricula: str, universidad_id: UUID
    ) -> Optional[Estudiante]:
        """Busca estudiante por matrícula en una universidad."""
        result = await self.db.execute(
            select(Estudiante).where(
                Estudiante.matricula == matricula,
                Estudiante.universidad_id == universidad_id
            )
        )
        return result.scalar_one_or_none()
