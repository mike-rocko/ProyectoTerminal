"""
API endpoints para administración de universidades.
Panel de admin para gestionar información, carreras y documentos.
"""
from fastapi import APIRouter, Depends, HTTPException, UploadFile, File, Form
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func
from typing import List, Optional
from pydantic import BaseModel, EmailStr
import logging

from app.core.dependencies import get_db
from app.core.security import get_password_hash, verify_password, create_access_token
from app.models import Universidad, Carrera, Estudiante, UniversidadInfo, AdminUniversidad
from app.services.cache_service import cache, CacheService

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/api/v1/admin", tags=["admin"])


# ============================================
# Schemas
# ============================================

class AdminRegisterRequest(BaseModel):
    email: EmailStr
    password: str
    nombre: str
    universidad_slug: str


class AdminLoginRequest(BaseModel):
    email: EmailStr
    password: str


class AdminResponse(BaseModel):
    id: str
    email: str
    nombre: str
    universidad_id: str
    universidad_nombre: str
    is_super_admin: bool


class UniversidadUpdateRequest(BaseModel):
    nombre: Optional[str] = None
    logo_url: Optional[str] = None
    email_contacto: Optional[str] = None
    telefono: Optional[str] = None
    direccion: Optional[str] = None
    config: Optional[dict] = None


class CarreraCreateRequest(BaseModel):
    nombre: str
    clave: str
    plan_estudios: Optional[dict] = None


class InfoDocumentoRequest(BaseModel):
    tipo: str  # mision, vision, calendario, reglamento, faq, contacto
    titulo: str
    contenido: str
    metadata: Optional[dict] = None


class DashboardStats(BaseModel):
    total_estudiantes: int
    total_carreras: int
    total_documentos: int
    estudiantes_activos_mes: int


# ============================================
# Auth Admin
# ============================================

@router.post("/register")
async def register_admin(request: AdminRegisterRequest, db: AsyncSession = Depends(get_db)):
    """Registra un nuevo administrador de universidad."""
    # Buscar universidad
    result = await db.execute(
        select(Universidad).where(Universidad.slug == request.universidad_slug)
    )
    universidad = result.scalar_one_or_none()
    
    if not universidad:
        raise HTTPException(status_code=404, detail="Universidad no encontrada")
    
    # Verificar email único
    result = await db.execute(
        select(AdminUniversidad).where(AdminUniversidad.email == request.email)
    )
    existing = result.scalar_one_or_none()
    
    if existing:
        raise HTTPException(status_code=400, detail="Email ya registrado")
    
    # Verificar si es el primer admin (será super_admin)
    result = await db.execute(
        select(func.count(AdminUniversidad.id)).where(
            AdminUniversidad.universidad_id == universidad.id
        )
    )
    admin_count = result.scalar() or 0
    
    # Crear admin
    admin = AdminUniversidad(
        email=request.email,
        password_hash=get_password_hash(request.password),
        nombre=request.nombre,
        universidad_id=universidad.id,
        is_super_admin=(admin_count == 0)  # Primer admin es super
    )
    
    db.add(admin)
    await db.commit()
    await db.refresh(admin)
    
    # Generar token
    token = create_access_token({
        "sub": str(admin.id),
        "universidad_id": str(admin.universidad_id),
        "email": admin.email,
        "type": "admin"
    })
    
    return {
        "token": {
            "access_token": token,
            "token_type": "bearer"
        },
        "admin": {
            "id": str(admin.id),
            "email": admin.email,
            "nombre": admin.nombre,
            "universidad_id": str(admin.universidad_id),
            "universidad_nombre": universidad.nombre,
            "is_super_admin": admin.is_super_admin
        }
    }


@router.post("/login")
async def login_admin(request: AdminLoginRequest, db: AsyncSession = Depends(get_db)):
    """Login de administrador."""
    result = await db.execute(
        select(AdminUniversidad).where(
            AdminUniversidad.email == request.email,
            AdminUniversidad.is_active == True
        )
    )
    admin = result.scalar_one_or_none()
    
    if not admin or not verify_password(request.password, admin.password_hash):
        raise HTTPException(status_code=401, detail="Credenciales inválidas")
    
    result = await db.execute(
        select(Universidad).where(Universidad.id == admin.universidad_id)
    )
    universidad = result.scalar_one_or_none()
    
    token = create_access_token({
        "sub": str(admin.id),
        "universidad_id": str(admin.universidad_id),
        "email": admin.email,
        "type": "admin"
    })
    
    return {
        "token": {
            "access_token": token,
            "token_type": "bearer"
        },
        "admin": {
            "id": str(admin.id),
            "email": admin.email,
            "nombre": admin.nombre,
            "universidad_id": str(admin.universidad_id),
            "universidad_nombre": universidad.nombre if universidad else "N/A",
            "is_super_admin": admin.is_super_admin
        }
    }


# ============================================
# Universidad Info
# ============================================

@router.get("/universidad/{universidad_id}")
async def get_universidad(universidad_id: str, db: AsyncSession = Depends(get_db)):
    """Obtiene información de la universidad (con caché)."""
    # Intentar obtener del caché
    cache_key = cache.key_universidad(universidad_id)
    cached = await cache.get(cache_key)
    if cached:
        return cached
    
    result = await db.execute(
        select(Universidad).where(Universidad.id == universidad_id)
    )
    universidad = result.scalar_one_or_none()
    
    if not universidad:
        raise HTTPException(status_code=404, detail="Universidad no encontrada")
    
    response = {
        "id": str(universidad.id),
        "nombre": universidad.nombre,
        "slug": universidad.slug,
        "logo_url": universidad.logo_url,
        "email_contacto": universidad.email_contacto,
        "telefono": universidad.telefono,
        "direccion": universidad.direccion,
        "config": universidad.config
    }
    
    # Guardar en caché (1 hora)
    await cache.set(cache_key, response, CacheService.TTL_LONG)
    return response


@router.put("/universidad/{universidad_id}")
async def update_universidad(
    universidad_id: str,
    request: UniversidadUpdateRequest,
    db: AsyncSession = Depends(get_db)
):
    """Actualiza información de la universidad."""
    result = await db.execute(
        select(Universidad).where(Universidad.id == universidad_id)
    )
    universidad = result.scalar_one_or_none()
    
    if not universidad:
        raise HTTPException(status_code=404, detail="Universidad no encontrada")
    
    # Actualizar campos proporcionados
    update_data = request.dict(exclude_unset=True, exclude_none=True)
    for field, value in update_data.items():
        setattr(universidad, field, value)
    
    await db.commit()
    
    # Invalidar caché
    await cache.delete(cache.key_universidad(universidad_id))
    
    return {"success": True, "message": "Universidad actualizada"}


# ============================================
# Carreras
# ============================================

@router.get("/universidad/{universidad_id}/carreras")
async def list_carreras(universidad_id: str, db: AsyncSession = Depends(get_db)):
    """Lista las carreras de una universidad (con caché)."""
    # Intentar obtener del caché
    cache_key = cache.key_carreras(universidad_id)
    cached = await cache.get(cache_key)
    if cached:
        return cached
    
    result = await db.execute(
        select(Carrera).where(Carrera.universidad_id == universidad_id)
    )
    carreras = result.scalars().all()
    
    response = {
        "carreras": [
            {
                "id": str(c.id),
                "nombre": c.nombre,
                "clave": c.clave,
                "tiene_plan": c.plan_estudios is not None
            }
            for c in carreras
        ]
    }
    
    # Guardar en caché (5 minutos)
    await cache.set(cache_key, response, CacheService.TTL_MEDIUM)
    return response


@router.post("/universidad/{universidad_id}/carreras")
async def create_carrera(
    universidad_id: str,
    request: CarreraCreateRequest,
    db: AsyncSession = Depends(get_db)
):
    """Crea una nueva carrera."""
    # Verificar universidad existe
    result = await db.execute(
        select(Universidad).where(Universidad.id == universidad_id)
    )
    universidad = result.scalar_one_or_none()
    
    if not universidad:
        raise HTTPException(status_code=404, detail="Universidad no encontrada")
    
    # Verificar clave única
    result = await db.execute(
        select(Carrera).where(
            Carrera.universidad_id == universidad_id,
            Carrera.clave == request.clave
        )
    )
    existing = result.scalar_one_or_none()
    
    if existing:
        raise HTTPException(status_code=400, detail="Ya existe una carrera con esa clave")
    
    carrera = Carrera(
        universidad_id=universidad_id,
        nombre=request.nombre,
        clave=request.clave,
        plan_estudios=request.plan_estudios
    )
    
    db.add(carrera)
    await db.commit()
    await db.refresh(carrera)
    
    # Invalidar caché de carreras
    await cache.delete(cache.key_carreras(universidad_id))
    
    return {
        "success": True,
        "carrera": {
            "id": str(carrera.id),
            "nombre": carrera.nombre,
            "clave": carrera.clave
        }
    }


@router.put("/universidad/{universidad_id}/carreras/{carrera_id}/plan")
async def update_plan_estudios(
    universidad_id: str,
    carrera_id: str,
    plan_estudios: dict,
    db: AsyncSession = Depends(get_db)
):
    """Actualiza el plan de estudios (mapa curricular) de una carrera."""
    result = await db.execute(
        select(Carrera).where(
            Carrera.id == carrera_id,
            Carrera.universidad_id == universidad_id
        )
    )
    carrera = result.scalar_one_or_none()
    
    if not carrera:
        raise HTTPException(status_code=404, detail="Carrera no encontrada")
    
    carrera.plan_estudios = plan_estudios
    await db.commit()
    
    # Invalidar caché
    await cache.delete(cache.key_carreras(universidad_id))
    
    return {"success": True, "message": "Plan de estudios actualizado"}


# ============================================
# Documentos RAG
# ============================================

@router.get("/universidad/{universidad_id}/documentos")
async def list_documentos(universidad_id: str, db: AsyncSession = Depends(get_db)):
    """Lista los documentos de información de la universidad (con caché)."""
    # Intentar obtener del caché
    cache_key = cache.key_documentos(universidad_id)
    cached = await cache.get(cache_key)
    if cached:
        return cached
    
    result = await db.execute(
        select(UniversidadInfo).where(UniversidadInfo.universidad_id == universidad_id)
    )
    docs = result.scalars().all()
    
    response = {
        "documentos": [
            {
                "id": str(d.id),
                "tipo": d.tipo,
                "titulo": d.titulo,
                "contenido_preview": d.contenido[:200] + "..." if len(d.contenido) > 200 else d.contenido,
                "created_at": d.created_at.isoformat() if d.created_at else None
            }
            for d in docs
        ]
    }
    
    # Guardar en caché (5 minutos)
    await cache.set(cache_key, response, CacheService.TTL_MEDIUM)
    return response


@router.post("/universidad/{universidad_id}/documentos")
async def create_documento(
    universidad_id: str,
    request: InfoDocumentoRequest,
    db: AsyncSession = Depends(get_db)
):
    """Crea un nuevo documento de información y genera embeddings."""
    # Verificar universidad
    result = await db.execute(
        select(Universidad).where(Universidad.id == universidad_id)
    )
    universidad = result.scalar_one_or_none()
    
    if not universidad:
        raise HTTPException(status_code=404, detail="Universidad no encontrada")
    
    try:
        # Crear documento sin embeddings por ahora debido a rate limits
        doc = UniversidadInfo(
            universidad_id=universidad_id,
            tipo=request.tipo,
            titulo=request.titulo,
            contenido=request.contenido,
            metadata=request.metadata or {}
        )
        db.add(doc)
        await db.commit()
        await db.refresh(doc)
        
        # Invalidar caché de documentos y respuestas RAG
        await cache.delete(cache.key_documentos(universidad_id))
        await cache.invalidate_pattern(f"rag:{universidad_id}")
        
        return {
            "success": True,
            "documento_id": str(doc.id),
            "message": "Documento creado correctamente"
        }
        
    except Exception as e:
        logger.exception(f"Error creando documento: {e}")
        raise HTTPException(status_code=500, detail="Error al crear documento")


@router.delete("/universidad/{universidad_id}/documentos/{documento_id}")
async def delete_documento(
    universidad_id: str,
    documento_id: str,
    db: AsyncSession = Depends(get_db)
):
    """Elimina un documento."""
    result = await db.execute(
        select(UniversidadInfo).where(
            UniversidadInfo.id == documento_id,
            UniversidadInfo.universidad_id == universidad_id
        )
    )
    doc = result.scalar_one_or_none()
    
    if not doc:
        raise HTTPException(status_code=404, detail="Documento no encontrado")
    
    await db.delete(doc)
    await db.commit()
    
    # Invalidar caché de documentos y respuestas RAG
    await cache.delete(cache.key_documentos(universidad_id))
    await cache.invalidate_pattern(f"rag:{universidad_id}")
    
    return {"success": True, "message": "Documento eliminado"}


# ============================================
# Dashboard / Métricas
# ============================================

@router.get("/universidad/{universidad_id}/dashboard")
async def get_dashboard(universidad_id: str, db: AsyncSession = Depends(get_db)):
    """Obtiene estadísticas del dashboard (con caché corto)."""
    # Intentar obtener del caché (1 minuto para stats)
    cache_key = cache.key_dashboard(universidad_id)
    cached = await cache.get(cache_key)
    if cached:
        return cached
    
    # Total estudiantes
    result = await db.execute(
        select(func.count(Estudiante.id)).where(
            Estudiante.universidad_id == universidad_id
        )
    )
    total_estudiantes = result.scalar() or 0
    
    # Total carreras
    result = await db.execute(
        select(func.count(Carrera.id)).where(
            Carrera.universidad_id == universidad_id
        )
    )
    total_carreras = result.scalar() or 0
    
    # Total documentos
    result = await db.execute(
        select(func.count(UniversidadInfo.id)).where(
            UniversidadInfo.universidad_id == universidad_id
        )
    )
    total_documentos = result.scalar() or 0
    
    # Estudiantes activos (registrados este mes) - simplificado
    from datetime import datetime
    inicio_mes = datetime.now().replace(day=1, hour=0, minute=0, second=0, microsecond=0)
    
    result = await db.execute(
        select(func.count(Estudiante.id)).where(
            Estudiante.universidad_id == universidad_id,
            Estudiante.created_at >= inicio_mes
        )
    )
    estudiantes_mes = result.scalar() or 0
    
    response = {
        "total_estudiantes": total_estudiantes,
        "total_carreras": total_carreras,
        "total_documentos": total_documentos,
        "estudiantes_activos_mes": estudiantes_mes,
        "universidad_id": universidad_id
    }
    
    # Guardar en caché (1 minuto - stats cambian frecuentemente)
    await cache.set(cache_key, response, CacheService.TTL_SHORT)
    return response


# ============================================
# Crear Universidad (Super Admin / Sistema)
# ============================================

class UniversidadCreateRequest(BaseModel):
    nombre: str
    slug: str
    email_contacto: Optional[str] = None
    telefono: Optional[str] = None


@router.post("/universidades")
async def create_universidad(request: UniversidadCreateRequest, db: AsyncSession = Depends(get_db)):
    """Crea una nueva universidad en el sistema."""
    # Verificar slug único
    result = await db.execute(
        select(Universidad).where(Universidad.slug == request.slug)
    )
    existing = result.scalar_one_or_none()
    
    if existing:
        raise HTTPException(status_code=400, detail="Ya existe una universidad con ese slug")
    
    universidad = Universidad(
        nombre=request.nombre,
        slug=request.slug,
        email_contacto=request.email_contacto,
        telefono=request.telefono
    )
    
    db.add(universidad)
    await db.commit()
    await db.refresh(universidad)
    
    return {
        "success": True,
        "universidad": {
            "id": str(universidad.id),
            "nombre": universidad.nombre,
            "slug": universidad.slug
        }
    }


@router.get("/universidades")
async def list_universidades(db: AsyncSession = Depends(get_db)):
    """Lista todas las universidades del sistema."""
    result = await db.execute(select(Universidad))
    universidades = result.scalars().all()
    
    return {
        "universidades": [
            {
                "id": str(u.id),
                "nombre": u.nombre,
                "slug": u.slug,
                "logo_url": u.logo_url
            }
            for u in universidades
        ]
    }
