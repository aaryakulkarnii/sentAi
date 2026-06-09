"""Async Kafka consumer – reads events and runs the processing pipeline."""

import asyncio
import json
from typing import Any

import structlog

from app.core.config import settings
from app.ingestion.pipeline import process_raw_event

logger = structlog.get_logger(__name__)

_consumer: Any | None = None
_task: asyncio.Task | None = None

TOPICS = [
    "sentinelai.sysmon",
    "sentinelai.auditd",
    "sentinelai.cloudtrail",
    "sentinelai.network",
]


async def _consume():
    assert _consumer is not None
    async for msg in _consumer:
        try:
            raw = json.loads(msg.value.decode("utf-8"))
            source = msg.topic.split(".")[-1]
            await process_raw_event(source, raw)
        except Exception as exc:
            logger.error("consume_error", topic=msg.topic, error=str(exc))


async def start_kafka_consumer() -> None:
    global _consumer, _task
    from aiokafka import AIOKafkaConsumer

    _consumer = AIOKafkaConsumer(
        *TOPICS,
        bootstrap_servers=settings.KAFKA_BOOTSTRAP_SERVERS,
        group_id=settings.KAFKA_CONSUMER_GROUP,
        auto_offset_reset="latest",
    )
    await _consumer.start()
    _task = asyncio.create_task(_consume())
    logger.info("kafka_consumer_started", topics=TOPICS)


async def stop_kafka_consumer() -> None:
    global _consumer, _task
    if _task:
        _task.cancel()
        try:
            await _task
        except asyncio.CancelledError:
            pass
        _task = None
    if _consumer:
        await _consumer.stop()
        _consumer = None
