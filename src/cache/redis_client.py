import json
import logging
from typing import Any, Optional

import redis.asyncio as redis

from src.config import Settings

logger = logging.getLogger(__name__)

settings = Settings()

CACHE_TTL = 3600

redis_client = redis.from_url(
    settings.redis_url,
    decode_responses=True,
)


async def get_redis() -> redis.Redis:
    return redis_client


class RedisClient:
    def __init__(self, client: redis.Redis) -> None:
        self._redis = client

    async def get_cached(self, key: str) -> Optional[dict[str, Any] | list[Any]]:
        try:
            data = await self._redis.get(key)
            if data is None:
                return None
            return json.loads(data)
        except Exception:
            logger.warning("Cache get failed for key=%s", key)
            return None

    async def set_cached(self, key: str, value: dict[str, Any] | list[Any]) -> None:
        try:
            await self._redis.set(key, json.dumps(value), ex=CACHE_TTL)
        except Exception:
            logger.warning("Cache set failed for key=%s", key)

    async def delete_cached(self, key: str) -> None:
        try:
            await self._redis.delete(key)
        except Exception:
            logger.warning("Cache delete failed for key=%s", key)

    async def delete_cached_pattern(self, pattern: str) -> None:
        try:
            async for key in self._redis.scan_iter(match=pattern):
                await self._redis.delete(key)
        except Exception:
            logger.warning("Cache delete pattern failed for pattern=%s", pattern)
