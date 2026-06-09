"""Application startup and shutdown hooks."""

import structlog

from app.api.ws.alerts import broadcast_alert
from app.core.config import settings
from app.db.opensearch import init_opensearch
from app.db.postgres import init_db
from app.db.qdrant import init_qdrant
from app.db.redis import init_redis
from app.ingestion.enrichment import init_geoip
from app.ingestion.kafka_consumer import start_kafka_consumer, stop_kafka_consumer
from app.ingestion.pipeline import init_engines
from app.services.detection.behavioral import BehavioralEngine
from app.services.detection.sigma_engine import SigmaEngine
from app.services.indexing import ensure_index_templates
from app.services.pubsub import register_listener, start_alert_subscriber, stop_alert_subscriber

logger = structlog.get_logger(__name__)


async def on_startup() -> None:
    logger.info("Starting SentinelAI backend")
    await init_db()
    await init_redis()
    await init_opensearch()
    await init_qdrant()
    init_geoip()
    await ensure_index_templates()

    sigma = SigmaEngine(rules_dir=settings.SIGMA_RULES_DIR)
    behavioral = BehavioralEngine()
    init_engines(sigma, behavioral)
    logger.info("detection_engines_ready", sigma_rules=len(sigma.rules))

    register_listener(broadcast_alert)
    await start_alert_subscriber()
    await start_kafka_consumer()
    logger.info("All services initialised")


async def on_shutdown() -> None:
    await stop_kafka_consumer()
    await stop_alert_subscriber()
    logger.info("SentinelAI backend stopped")
