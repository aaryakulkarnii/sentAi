"""Redis async client."""

import redis.asyncio as aioredis

from app.core.config import settings

_pool: aioredis.Redis | None = None


async def init_redis() -> None:
    global _pool
    _pool = aioredis.Redis(
        host=settings.REDIS_HOST,
        port=settings.REDIS_PORT,
        password=settings.REDIS_PASSWORD or None,
        decode_responses=True,
    )


def get_redis() -> aioredis.Redis:
    if _pool is None:
        raise RuntimeError("Redis not initialised")
    return _pool
