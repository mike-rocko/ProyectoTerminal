"""
Dependencies de FastAPI para inyección de dependencias.
"""
from typing import Optional
from uuid import UUID

from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from app.db.session import get_db
from app.core.security import verify_token
from app.models.estudiante import Estudiante
from app.models.universidad import Universidad


# Esquema de autenticación Bearer
security = HTTPBearer(auto_error=False)


async def get_current_user(
    credentials: Optional[HTTPAuthorizationCredentials] = Depends(security),
    db: AsyncSession = Depends(get_db)
) -> Estudiante:
    """
    Dependency que obtiene el usuario actual desde el token JWT.
    
    Uso:
        @app.get("/ruta-protegida")
        async def ruta(user: Estudiante = Depends(get_current_user)):
            ...
    
    Raises:
        HTTPException 401: Si no hay token o es inválido
        HTTPException 404: Si el usuario no existe
    """
    if credentials is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Token de autenticación requerido",
            headers={"WWW-Authenticate": "Bearer"}
        )
    
    token = credentials.credentials
    token_data = verify_token(token)
    
    if token_data is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Token inválido o expirado",
            headers={"WWW-Authenticate": "Bearer"}
        )
    
    # Buscar estudiante en la base de datos
    estudiante_id = UUID(token_data["estudiante_id"])
    result = await db.execute(
        select(Estudiante).where(Estudiante.id == estudiante_id)
    )
    estudiante = result.scalar_one_or_none()
    
    if estudiante is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Usuario no encontrado"
        )
    
    if not estudiante.is_active:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Usuario desactivado"
        )
    
    return estudiante


async def get_current_user_optional(
    credentials: Optional[HTTPAuthorizationCredentials] = Depends(security),
    db: AsyncSession = Depends(get_db)
) -> Optional[Estudiante]:
    """
    Dependency que obtiene el usuario actual si existe token.
    No lanza error si no hay token, retorna None.
    
    Útil para endpoints que funcionan diferente si hay usuario o no.
    """
    if credentials is None:
        return None
    
    try:
        return await get_current_user(credentials, db)
    except HTTPException:
        return None


async def get_current_universidad(
    user: Estudiante = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
) -> Universidad:
    """
    Dependency que obtiene la universidad del usuario actual.
    
    Uso para operaciones multi-tenant:
        @app.get("/carreras")
        async def get_carreras(uni: Universidad = Depends(get_current_universidad)):
            # Solo retorna carreras de esta universidad
            ...
    """
    result = await db.execute(
        select(Universidad).where(Universidad.id == user.universidad_id)
    )
    universidad = result.scalar_one_or_none()
    
    if universidad is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Universidad no encontrada"
        )
    
    return universidad


def require_verified_user(user: Estudiante = Depends(get_current_user)) -> Estudiante:
    """
    Dependency que requiere un usuario verificado.
    
    Uso para endpoints que requieren email verificado.
    """
    if not user.is_verified:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Email no verificado. Por favor verifica tu email."
        )
    return user
