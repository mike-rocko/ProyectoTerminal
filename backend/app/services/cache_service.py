"""
Servicio de caché con Redis para mejorar rendimiento.
Cachea consultas frecuentes: universidad info, carreras, dashboard, respuestas RAG.
"""
import json
import hashlib
import logging
from typing import Optional, Any, Callable
from functools import wraps
import redis.asyncio as redis
from app.core.config import settings

logger = logging.getLogger(__name__)


class CacheService:
    """Servicio de caché usando Redis."""
    
    # TTL (Time To Live) en segundos
    TTL_SHORT = 60          # 1 minuto - datos que cambian frecuentemente
    TTL_MEDIUM = 300        # 5 minutos - datos moderados
    TTL_LONG = 3600         # 1 hora - datos que cambian poco
    TTL_DAY = 86400         # 24 horas - datos casi estáticos
    
    def __init__(self):
        self._client: Optional[redis.Redis] = None
        self._connected = False
    
    async def connect(self) -> bool:
        """Conecta a Redis."""
        if self._connected and self._client:
            return True
        
        try:
            self._client = redis.from_url(
                settings.redis_url,
                encoding="utf-8",
                decode_responses=True
            )
            # Test connection
            await self._client.ping()
            self._connected = True
            logger.info("✅ Conectado a Redis")
            return True
        except Exception as e:
            logger.warning(f"⚠️ Redis no disponible: {e}. Funcionando sin caché.")
            self._connected = False
            return False
    
    async def disconnect(self):
        """Desconecta de Redis."""
        if self._client:
            await self._client.close()
            self._connected = False
    
    def _make_key(self, prefix: str, *args, **kwargs) -> str:
        """Genera una clave única para el caché."""
        # Crear hash de los argumentos
        key_data = json.dumps({"args": args, "kwargs": kwargs}, sort_keys=True)
        key_hash = hashlib.md5(key_data.encode()).hexdigest()[:12]
        return f"tutor_ia:{prefix}:{key_hash}"
    
    async def get(self, key: str) -> Optional[Any]:
        """Obtiene un valor del caché."""
        if not self._connected:
            await self.connect()
        
        if not self._connected:
            return None
        
        try:
            value = await self._client.get(key)
            if value:
                logger.debug(f"🎯 Cache HIT: {key}")
                return json.loads(value)
            logger.debug(f"❌ Cache MISS: {key}")
            return None
        except Exception as e:
            logger.warning(f"Error leyendo caché: {e}")
            return None
    
    async def set(self, key: str, value: Any, ttl: int = TTL_MEDIUM) -> bool:
        """Guarda un valor en el caché."""
        if not self._connected:
            await self.connect()
        
        if not self._connected:
            return False
        
        try:
            await self._client.setex(key, ttl, json.dumps(value))
            logger.debug(f"💾 Cache SET: {key} (TTL: {ttl}s)")
            return True
        except Exception as e:
            logger.warning(f"Error escribiendo caché: {e}")
            return False
    
    async def delete(self, key: str) -> bool:
        """Elimina una clave del caché."""
        if not self._connected:
            return False
        
        try:
            await self._client.delete(key)
            logger.debug(f"🗑️ Cache DELETE: {key}")
            return True
        except Exception as e:
            logger.warning(f"Error eliminando caché: {e}")
            return False
    
    async def invalidate_pattern(self, pattern: str) -> int:
        """Invalida todas las claves que coincidan con un patrón."""
        if not self._connected:
            await self.connect()
        
        if not self._connected:
            return 0
        
        try:
            keys = []
            async for key in self._client.scan_iter(match=f"tutor_ia:{pattern}:*"):
                keys.append(key)
            
            if keys:
                await self._client.delete(*keys)
                logger.info(f"🗑️ Invalidadas {len(keys)} claves con patrón: {pattern}")
            return len(keys)
        except Exception as e:
            logger.warning(f"Error invalidando caché: {e}")
            return 0
    
    # ============================================
    # Claves específicas por entidad
    # ============================================
    
    def key_universidad(self, universidad_id: str) -> str:
        """Clave para info de universidad."""
        return f"tutor_ia:universidad:{universidad_id}"
    
    def key_carreras(self, universidad_id: str) -> str:
        """Clave para carreras de universidad."""
        return f"tutor_ia:carreras:{universidad_id}"
    
    def key_documentos(self, universidad_id: str) -> str:
        """Clave para documentos de universidad."""
        return f"tutor_ia:documentos:{universidad_id}"
    
    def key_dashboard(self, universidad_id: str) -> str:
        """Clave para dashboard de universidad."""
        return f"tutor_ia:dashboard:{universidad_id}"
    
    def key_rag_response(self, universidad_id: str, query: str) -> str:
        """Clave para respuestas RAG (por query normalizada)."""
        # Normalizar query: lowercase, sin espacios extra
        normalized = " ".join(query.lower().split())
        query_hash = hashlib.md5(normalized.encode()).hexdigest()[:16]
        return f"tutor_ia:rag:{universidad_id}:{query_hash}"
    
    # ============================================
    # Métodos de alto nivel
    # ============================================
    
    async def get_or_set(
        self, 
        key: str, 
        factory: Callable, 
        ttl: int = TTL_MEDIUM
    ) -> Any:
        """
        Obtiene del caché o ejecuta factory y guarda el resultado.
        Patrón Cache-Aside.
        """
        # Intentar obtener del caché
        cached = await self.get(key)
        if cached is not None:
            return cached
        
        # Ejecutar factory (puede ser async)
        if callable(factory):
            import asyncio
            if asyncio.iscoroutinefunction(factory):
                result = await factory()
            else:
                result = factory()
        else:
            result = factory
        
        # Guardar en caché
        await self.set(key, result, ttl)
        return result
    
    async def invalidate_universidad(self, universidad_id: str):
        """Invalida todo el caché de una universidad."""
        patterns = [
            f"universidad:{universidad_id}",
            f"carreras:{universidad_id}",
            f"documentos:{universidad_id}",
            f"dashboard:{universidad_id}",
        ]
        for pattern in patterns:
            await self.delete(f"tutor_ia:{pattern}")
        
        # También invalidar respuestas RAG
        await self.invalidate_pattern(f"rag:{universidad_id}")
        
        logger.info(f"🔄 Caché invalidado para universidad: {universidad_id}")


# Singleton
cache = CacheService()


# ============================================
# Decorador para cachear funciones
# ============================================

def cached(prefix: str, ttl: int = CacheService.TTL_MEDIUM):
    """
    Decorador para cachear resultados de funciones async.
    
    Uso:
        @cached("mi_funcion", ttl=300)
        async def mi_funcion(param1, param2):
            ...
    """
    def decorator(func: Callable):
        @wraps(func)
        async def wrapper(*args, **kwargs):
            # Generar clave única
            key = cache._make_key(prefix, *args, **kwargs)
            
            # Intentar obtener del caché
            cached_result = await cache.get(key)
            if cached_result is not None:
                return cached_result
            
            # Ejecutar función
            result = await func(*args, **kwargs)
            
            # Guardar en caché (solo si no es error)
            if result and not (isinstance(result, dict) and "error" in result):
                await cache.set(key, result, ttl)
            
            return result
        
        return wrapper
    return decorator
