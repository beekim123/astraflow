import asyncio
import time
from typing import Any

import redis.asyncio as redis

from app.core.config import settings


class MemoryCache:
    """Small async in-memory fallback for tests or when Redis is unavailable."""

    def __init__(self) -> None:
        self._data: dict[str, tuple[Any, float | None]] = {}
        self._lock = asyncio.Lock()

    async def set(self, key: str, value: Any, ex: int | None = None) -> None:
        expires_at = time.time() + ex if ex else None
        async with self._lock:
            self._data[key] = (value, expires_at)

    async def get(self, key: str) -> Any | None:
        async with self._lock:
            item = self._data.get(key)
            if item is None:
                return None
            value, expires_at = item
            if expires_at and expires_at < time.time():
                self._data.pop(key, None)
                return None
            return value

    async def delete(self, key: str) -> None:
        async with self._lock:
            self._data.pop(key, None)

    async def incr(self, key: str, ex: int | None = None) -> int:
        current = await self.get(key)
        value = int(current or 0) + 1
        await self.set(key, value, ex=ex)
        return value


redis_client = redis.from_url(settings.redis_url, decode_responses=True)
memory_cache = MemoryCache()


async def cache_set(key: str, value: Any, ex: int | None = None) -> None:
    try:
        await redis_client.set(key, value, ex=ex)
    except Exception:
        await memory_cache.set(key, value, ex=ex)


async def cache_get(key: str) -> Any | None:
    try:
        return await redis_client.get(key)
    except Exception:
        return await memory_cache.get(key)


async def cache_delete(key: str) -> None:
    try:
        await redis_client.delete(key)
    except Exception:
        await memory_cache.delete(key)


async def cache_incr(key: str, ex: int | None = None) -> int:
    try:
        value = await redis_client.incr(key)
        if ex:
            await redis_client.expire(key, ex)
        return int(value)
    except Exception:
        return await memory_cache.incr(key, ex=ex)

