"""
Módulo de seguridad: hashing de contraseñas y manejo de JWT.
"""
from datetime import datetime, timedelta, timezone
from typing import Optional
from uuid import UUID

from passlib.context import CryptContext
from jose import JWTError, jwt

from app.core.config import settings


# ============================================
# Configuración de Hashing (bcrypt)
# ============================================
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


def hash_password(password: str) -> str:
    """
    Genera hash bcrypt de una contraseña.
    
    Args:
        password: Contraseña en texto plano
        
    Returns:
        Hash bcrypt de la contraseña
    """
    return pwd_context.hash(password)


# Alias para compatibilidad
get_password_hash = hash_password


def verify_password(plain_password: str, hashed_password: str) -> bool:
    """
    Verifica si una contraseña coincide con su hash.
    
    Args:
        plain_password: Contraseña en texto plano
        hashed_password: Hash almacenado en la DB
        
    Returns:
        True si coinciden, False si no
    """
    return pwd_context.verify(plain_password, hashed_password)


# ============================================
# Manejo de JWT
# ============================================
def create_access_token(
    data: dict = None,
    estudiante_id: UUID = None,
    universidad_id: UUID = None,
    email: str = None,
    expires_delta: Optional[timedelta] = None
) -> str:
    """
    Crea un token JWT para autenticación.
    
    Args:
        data: Dict con datos a incluir en el token (modo flexible)
        estudiante_id: ID del estudiante (modo legacy)
        universidad_id: ID de la universidad (multi-tenant)
        email: Email del usuario
        expires_delta: Tiempo de expiración personalizado
        
    Returns:
        Token JWT codificado
    """
    if expires_delta:
        expire = datetime.now(timezone.utc) + expires_delta
    else:
        expire = datetime.now(timezone.utc) + timedelta(
            minutes=settings.access_token_expire_minutes
        )
    
    # Modo flexible: usar dict directamente
    if data is not None:
        to_encode = data.copy()
        to_encode["exp"] = expire
        to_encode["iat"] = datetime.now(timezone.utc)
    else:
        # Modo legacy: parámetros individuales
        to_encode = {
            "sub": str(estudiante_id) if estudiante_id else None,
            "universidad_id": str(universidad_id) if universidad_id else None,
            "email": email,
            "exp": expire,
            "iat": datetime.now(timezone.utc),
            "type": "access"
        }
    
    encoded_jwt = jwt.encode(
        to_encode,
        settings.jwt_secret_key,
        algorithm=settings.jwt_algorithm
    )
    
    return encoded_jwt


def decode_token(token: str) -> Optional[dict]:
    """
    Decodifica y valida un token JWT.
    
    Args:
        token: Token JWT a decodificar
        
    Returns:
        Payload del token si es válido, None si es inválido
    """
    try:
        payload = jwt.decode(
            token,
            settings.jwt_secret_key,
            algorithms=[settings.jwt_algorithm]
        )
        return payload
    except JWTError:
        return None


def verify_token(token: str) -> Optional[dict]:
    """
    Verifica un token y retorna los datos del usuario.
    
    Args:
        token: Token JWT
        
    Returns:
        Dict con sub (estudiante_id), universidad_id, email
        None si el token es inválido
    """
    payload = decode_token(token)
    
    if payload is None:
        return None
    
    # Verificar campos requeridos
    if "sub" not in payload or "universidad_id" not in payload:
        return None
    
    return {
        "estudiante_id": payload["sub"],
        "universidad_id": payload["universidad_id"],
        "email": payload.get("email")
    }
