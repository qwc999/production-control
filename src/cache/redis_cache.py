import json
from typing import Any

from redis.asyncio import Redis

from src.core.config import settings


class RedisCache:
    def __init__(self):
        self.redis = Redis.from_url(
            settings.redis_cache_url,
            decode_responses=True
        )

    async def get(self, key: str) -> Any | None:
        value = await self.redis.get(key)
        if value is None:
            return None
        return json.loads(value)

    async def set(self, key: str, value: Any, ttl: int) -> None:
        await self.redis.set(
            name=key,
            value=json.dumps(value, ensure_ascii=False),
            ex=ttl
        )

    async def delete(self, *keys: str) -> None:
        if keys:
            await self.redis.delete(*keys)

    async def delete_pattern(self, pattern: str) -> None:
        keys = []
        async for key in self.redis.scan_iter(match=pattern):
            keys.append(key)
        if keys:
            await self.redis.delete(*keys)

    async def close(self) -> None:
        await self.redis.aclose()
