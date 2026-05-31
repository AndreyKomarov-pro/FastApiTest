import json

import redis.asyncio as redis

from src.config import Settings

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

    async def get_cached(self, key: str) -> dict | list | None:
        data = await self._redis.get(key)
        if data is None:
            return None
        return json.loads(data)

    async def set_cached(self, key: str, value: dict | list) -> None:
        await self._redis.set(key, json.dumps(value), ex=CACHE_TTL)

    async def delete_cached(self, key: str) -> None:
        await self._redis.delete(key)

    async def delete_cached_pattern(self, pattern: str) -> None:
        async for key in self._redis.scan_iter(match=pattern):
            await self._redis.delete(key)
