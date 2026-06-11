"""Application startup and shutdown hooks."""

import structlog

from app.api.ws.alerts import broadcast_alert
from app.core.config import settings
from app.db.postgres import init_db
from app.db.redis import init_redis
from app.ingestion.enrichment import init_geoip
from app.ingestion.redis_consumer import start_redis_consumer, stop_redis_consumer
from app.ingestion.pipeline import init_engines
from app.services.detection.behavioral import BehavioralEngine
from app.services.detection.sigma_engine import SigmaEngine
from app.services.indexing import ensure_index_templates
from app.services.pubsub import register_listener, start_alert_subscriber, stop_alert_subscriber

logger = structlog.get_logger(__name__)


async def on_startup() -> None:
    mode = "DEV (zero-infra)" if settings.DEV_MODE else "PRODUCTION"
    logger.info("starting_sentinelai_backend", mode=mode)

    # Core stores (always needed). Redis is in-memory in DEV_MODE.
    await init_db()
    await init_redis()

    # Heavy infra — only in production. Each is best-effort so a missing
    # service degrades gracefully rather than crashing startup.
    if not settings.DEV_MODE:

        try:
            await ensure_index_templates()
        except Exception as exc:
            logger.warning("index_template_init_failed", error=str(exc))

    init_geoip()

    # Detection engines (work without external infra).
    sigma = SigmaEngine(rules_dir=settings.SIGMA_RULES_DIR)
    behavioral = BehavioralEngine()
    init_engines(sigma, behavioral)
    logger.info("detection_engines_ready", sigma_rules=len(sigma.rules))

    # Real-time alert delivery.
    register_listener(broadcast_alert)
    if not settings.DEV_MODE:
        await start_alert_subscriber()
        try:
            await start_redis_consumer()
        except Exception as exc:
            logger.warning("redis_consumer_unavailable", error=str(exc))

    logger.info("sentinelai_backend_ready", mode=mode)


async def on_shutdown() -> None:
    if not settings.DEV_MODE:
        await stop_redis_consumer()
        await stop_alert_subscriber()
    logger.info("sentinelai_backend_stopped")
