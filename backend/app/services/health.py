"""Dependency health probes for the /health endpoint."""

import structlog
from aiokafka.admin import AIOKafkaAdminClient
from sqlalchemy import text

from app.core.config import settings
from app.db.opensearch import get_opensearch
from app.db.postgres import engine
from app.db.qdrant import get_qdrant
from app.db.redis import get_redis

logger = structlog.get_logger(__name__)


async def check_postgres() -> dict:
    try:
        async with engine.connect() as conn:
            await conn.execute(text("SELECT 1"))
        return {"status": "ok"}
    except Exception as exc:
        logger.warning("health_postgres_failed", error=str(exc))
        return {"status": "error", "detail": str(exc)}


async def check_opensearch() -> dict:
    try:
        client = get_opensearch()
        health = await client.cluster.health()
        status = health.get("status", "unknown")
        if status == "red":
            return {"status": "error", "detail": f"cluster status: {status}"}
        return {"status": "ok", "cluster": status}
    except Exception as exc:
        logger.warning("health_opensearch_failed", error=str(exc))
        return {"status": "error", "detail": str(exc)}


async def check_redis() -> dict:
    try:
        redis = get_redis()
        pong = await redis.ping()
        if not pong:
            return {"status": "error", "detail": "ping returned false"}
        return {"status": "ok"}
    except Exception as exc:
        logger.warning("health_redis_failed", error=str(exc))
        return {"status": "error", "detail": str(exc)}


async def check_kafka() -> dict:
    admin = AIOKafkaAdminClient(bootstrap_servers=settings.KAFKA_BOOTSTRAP_SERVERS)
    try:
        await admin.start()
        topics = await admin.list_topics()
        return {"status": "ok", "topics": len(topics)}
    except Exception as exc:
        logger.warning("health_kafka_failed", error=str(exc))
        return {"status": "error", "detail": str(exc)}
    finally:
        await admin.close()


async def check_qdrant() -> dict:
    try:
        client = get_qdrant()
        collections = await client.get_collections()
        count = len(collections.collections)
        return {"status": "ok", "collections": count}
    except Exception as exc:
        logger.warning("health_qdrant_failed", error=str(exc))
        return {"status": "error", "detail": str(exc)}


async def run_health_checks() -> dict:
    postgres = await check_postgres()
    opensearch = await check_opensearch()
    redis = await check_redis()
    kafka = await check_kafka()
    qdrant = await check_qdrant()

    services = {
        "postgres": postgres,
        "opensearch": opensearch,
        "redis": redis,
        "kafka": kafka,
        "qdrant": qdrant,
    }
    all_ok = all(s["status"] == "ok" for s in services.values())
    return {
        "status": "ok" if all_ok else "degraded",
        "version": "0.1.0",
        "services": services,
    }
