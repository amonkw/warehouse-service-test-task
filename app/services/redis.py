import redis.asyncio as redis
from pydantic import BaseModel

from app.config import settings
import logging
import json
from typing import Any, Optional
from uuid import UUID

logger = logging.getLogger(__name__)
redis_client: Optional[redis.Redis] = None


async def get_redis_client() -> redis.Redis:
    """Возвращает (инициализирует при первом вызове) Redis клиент."""
    global redis_client
    if redis_client is None:
        try:
            redis_client = redis.from_url(
                settings.redis_url,
                encoding="utf-8",
                decode_responses=True,  # Важно для строк
            )
            await redis_client.ping()
            logger.info("Redis connection established.")
        except Exception as e:
            logger.error(f"Failed to connect to Redis: {e}", exc_info=True)
            # В реальном приложении можно добавить retry или fallback
            raise
    return redis_client


async def set_cache(key: str, value: Any, ttl: int = settings.CACHE_TTL_SECONDS):
    """Сохраняет значение в кэш."""
    try:
        client = await get_redis_client()
        # Сериализуем в JSON, если это не простая строка/число
        if isinstance(value, (dict, list, BaseModel)):
            value_str = json.dumps(value, default=str)  # default=str для UUID/datetime
        else:
            value_str = str(value)
        await client.setex(key, ttl, value_str)
        logger.debug(f"Cache SET for key: {key}")
    except Exception as e:
        logger.warning(f"Failed to set cache for key {key}: {e}")


async def get_cache(key: str) -> Optional[Any]:
    """Получает значение из кэша."""
    try:
        client = await get_redis_client()
        value = await client.get(key)
        if value:
            logger.debug(f"Cache HIT for key: {key}")
            # Пытаемся десериализовать JSON
            try:
                return json.loads(value)
            except json.JSONDecodeError:
                return value  # Возвращаем как есть, если не JSON
        logger.debug(f"Cache MISS for key: {key}")
        return None
    except Exception as e:
        logger.warning(f"Failed to get cache for key {key}: {e}")
        return None


async def invalidate_cache(*keys: str):
    """Удаляет ключи из кэша."""
    if not keys:
        return
    try:
        client = await get_redis_client()
        await client.delete(*keys)
        logger.debug(f"Cache INVALIDATED for keys: {keys}")
    except Exception as e:
        logger.warning(f"Failed to invalidate cache for keys {keys}: {e}")


# Функции для генерации ключей
def get_stock_cache_key(warehouse_id: UUID, product_id: UUID) -> str:
    return f"stock:{warehouse_id}:{product_id}"


def get_movement_cache_key(movement_id: UUID) -> str:
    return f"movement:{movement_id}"
