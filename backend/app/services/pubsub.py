"""Redis pub/sub for real-time alert broadcasting."""

from __future__ import annotations

import asyncio
import json
from collections.abc import Awaitable, Callable

import structlog

from app.core.config import settings
from app.db.redis import get_redis

logger = structlog.get_logger(__name__)

ALERTS_CHANNEL = "alerts:new"

_subscriber_task: asyncio.Task | None = None
_listeners: list[Callable[[dict], Awaitable[None]]] = []


def register_listener(handler: Callable[[dict], Awaitable[None]]) -> None:
    _listeners.append(handler)


async def _dispatch(alert_data: dict) -> None:
    for handler in _listeners:
        try:
            await handler(alert_data)
        except Exception as exc:
            logger.error("alert_listener_error", error=str(exc))


async def publish_alert(alert_data: dict) -> None:
    # DEV_MODE: dispatch in-process (no Redis pub/sub server).
    if settings.DEV_MODE or settings.REDIS_URL == "inmemory":
        await _dispatch(alert_data)
        return
    redis = get_redis()
    await redis.publish(ALERTS_CHANNEL, json.dumps(alert_data))


async def _subscribe_loop() -> None:
    redis = get_redis()
    pubsub = redis.pubsub()
    await pubsub.subscribe(ALERTS_CHANNEL)
    logger.info("alert_pubsub_subscribed", channel=ALERTS_CHANNEL)

    async for message in pubsub.listen():
        if message["type"] != "message":
            continue
        try:
            data = json.loads(message["data"])
            for handler in _listeners:
                await handler(data)
        except Exception as exc:
            logger.error("alert_pubsub_handler_error", error=str(exc))


async def start_alert_subscriber() -> None:
    global _subscriber_task
    if _subscriber_task is None:
        _subscriber_task = asyncio.create_task(_subscribe_loop())


async def stop_alert_subscriber() -> None:
    global _subscriber_task
    if _subscriber_task:
        _subscriber_task.cancel()
        try:
            await _subscriber_task
        except asyncio.CancelledError:
            pass
        _subscriber_task = None
