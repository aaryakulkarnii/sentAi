"""Dependency health probes for the /health endpoint."""

import structlog
from sqlalchemy import text

from app.core.config import settings
from app.db.postgres import engine
from app.db.redis import get_redis

logger = structlog.get_logger(__name__)

DISABLED = {"status": "disabled", "detail": "not used in DEV_MODE"}


async def check_database() -> dict:
    try:
        async with engine.connect() as conn:
            await conn.execute(text("SELECT 1"))
        backend = "sqlite" if settings.DEV_MODE else "postgres"
        return {"status": "ok", "backend": backend}
    except Exception as exc:
        logger.warning("health_db_failed", error=str(exc))
        return {"status": "error", "detail": str(exc)}


async def check_redis() -> dict:
    try:
        redis = get_redis()
        pong = await redis.ping()
        if not pong:
            return {"status": "error", "detail": "ping returned false"}
        backend = "in-memory" if settings.DEV_MODE else "redis"
        return {"status": "ok", "backend": backend}
    except Exception as exc:
        logger.warning("health_redis_failed", error=str(exc))
        return {"status": "error", "detail": str(exc)}


async def run_health_checks() -> dict:
    services = {
        "database": await check_database(),
        "redis": await check_redis(),
    }
    # "disabled" services don't count against health.
    all_ok = all(s["status"] in ("ok", "disabled") for s in services.values())
    return {
        "status": "ok" if all_ok else "degraded",
        "mode": "dev" if settings.DEV_MODE else "production",
        "version": "0.1.0",
        "services": services,
    }
