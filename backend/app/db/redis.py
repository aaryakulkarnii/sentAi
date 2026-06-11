"""Redis async client, with an in-memory shim for DEV_MODE (no server needed)."""

from __future__ import annotations

import time
from typing import Any

import structlog

from app.core.config import settings

logger = structlog.get_logger(__name__)

_pool: Any | None = None


# ── In-memory Redis (DEV_MODE) ──────────────────────────────────────────────
class _InMemoryPipeline:
    def __init__(self, redis: "InMemoryRedis"):
        self._redis = redis
        self._ops: list[tuple] = []

    def incr(self, key: str):
        self._ops.append(("incr", key))
        return self

    def expire(self, key: str, ttl: int):
        self._ops.append(("expire", key, ttl))
        return self

    async def execute(self) -> list:
        results = []
        for op in self._ops:
            if op[0] == "incr":
                results.append(await self._redis.incr(op[1]))
            elif op[0] == "expire":
                results.append(await self._redis.expire(op[1], op[2]))
        self._ops.clear()
        return results


class InMemoryRedis:
    """Minimal async Redis substitute covering the ops SentinelAI uses.

    Supports: set(nx, ex), get, delete, incr, expire, sadd, scard, pipeline.
    TTLs are honoured lazily on access. Pub/sub is handled in-process by the
    pubsub module in DEV_MODE, so it is intentionally not implemented here.
    """

    def __init__(self) -> None:
        self._store: dict[str, Any] = {}
        self._expiry: dict[str, float] = {}

    def _expired(self, key: str) -> bool:
        exp = self._expiry.get(key)
        if exp is not None and time.monotonic() > exp:
            self._store.pop(key, None)
            self._expiry.pop(key, None)
            return True
        return False

    async def set(self, key: str, value: Any, nx: bool = False, ex: int | None = None):
        if self._expired(key):
            pass
        if nx and key in self._store:
            return None
        self._store[key] = value
        if ex is not None:
            self._expiry[key] = time.monotonic() + ex
        return True

    async def get(self, key: str):
        if self._expired(key):
            return None
        return self._store.get(key)

    async def delete(self, *keys: str):
        n = 0
        for key in keys:
            if self._store.pop(key, None) is not None:
                n += 1
            self._expiry.pop(key, None)
        return n

    async def incr(self, key: str) -> int:
        if self._expired(key):
            pass
        val = int(self._store.get(key, 0)) + 1
        self._store[key] = val
        return val

    async def expire(self, key: str, ttl: int) -> bool:
        if key in self._store:
            self._expiry[key] = time.monotonic() + ttl
            return True
        return False

    async def sadd(self, key: str, *members: Any) -> int:
        if self._expired(key):
            pass
        s: set = self._store.setdefault(key, set())
        before = len(s)
        s.update(str(m) for m in members)
        return len(s) - before

    async def scard(self, key: str) -> int:
        if self._expired(key):
            return 0
        return len(self._store.get(key, set()))

    def pipeline(self) -> _InMemoryPipeline:
        return _InMemoryPipeline(self)

    async def ping(self) -> bool:
        return True

    async def aclose(self) -> None:  # pragma: no cover - cleanup noop
        self._store.clear()
        self._expiry.clear()


# ── Lifecycle ───────────────────────────────────────────────────────────────
async def init_redis() -> None:
    global _pool
    if settings.DEV_MODE:
        _pool = InMemoryRedis()
        logger.info("redis_in_memory_ready")
        return

    import redis.asyncio as aioredis

    _pool = aioredis.from_url(
        settings.REDIS_URL,
        decode_responses=True,
    )


def get_redis():
    if _pool is None:
        raise RuntimeError("Redis not initialised")
    return _pool
