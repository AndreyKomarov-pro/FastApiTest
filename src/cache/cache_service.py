import json

import redis.asyncio as redis

CACHE_TTL = 3600


class CacheService:
    def __init__(self, redis_client: redis.Redis) -> None:
        self.redis = redis_client

    async def get(self, key: str) -> dict | list | None:
        data = await self.redis.get(key)
        if data is None:
            return None
        return json.loads(data)

    async def set(self, key: str, value: dict | list) -> None:
        await self.redis.set(key, json.dumps(value), ex=CACHE_TTL)

    async def delete(self, key: str) -> None:
        await self.redis.delete(key)

    async def delete_pattern(self, pattern: str) -> None:
        async for key in self.redis.scan_iter(match=pattern):
            await self.redis.delete(key)
