"""Async Redis consumer – reads events and runs the processing pipeline."""

import asyncio
import json
import structlog

from app.ingestion.pipeline import process_raw_event
from app.db.redis import get_redis

logger = structlog.get_logger(__name__)

_pubsub = None
_task: asyncio.Task | None = None

TOPICS = [
    "sentinelai.sysmon",
    "sentinelai.auditd",
    "sentinelai.cloudtrail",
    "sentinelai.network",
]


async def _consume():
    assert _pubsub is not None
    async for msg in _pubsub.listen():
        if msg["type"] != "message":
            continue
        try:
            raw = json.loads(msg["data"])
            topic = msg["channel"].decode("utf-8")
            source = topic.split(".")[-1]
            await process_raw_event(source, raw)
        except Exception as exc:
            logger.error("redis_consume_error", error=str(exc))


async def start_redis_consumer() -> None:
    global _pubsub, _task
    r = get_redis()
    if r is None:
        return
    
    _pubsub = r.pubsub()
    await _pubsub.subscribe(*TOPICS)
    
    _task = asyncio.create_task(_consume())
    logger.info("redis_consumer_started", topics=TOPICS)


async def stop_redis_consumer() -> None:
    global _pubsub, _task
    if _task:
        _task.cancel()
        try:
            await _task
        except asyncio.CancelledError:
            pass
        _task = None
    if _pubsub:
        await _pubsub.unsubscribe()
        await _pubsub.close()
        _pubsub = None
