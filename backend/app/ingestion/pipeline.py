"""Event processing pipeline: enrich → index → detect → alert."""

from __future__ import annotations

import structlog

from app.ingestion.enrichment import enrich
from app.ingestion.normalizer import normalize
from app.ingestion.schema import NormalizedEvent
from app.services.alert_service import alert_service
from app.services.correlation.engine import handle_new_alert
from app.services.detection.behavioral import BehavioralEngine
from app.services.detection.sigma_engine import SigmaEngine
from app.services.indexing import index_event

logger = structlog.get_logger(__name__)

_sigma_engine: SigmaEngine | None = None
_behavioral_engine: BehavioralEngine | None = None


def init_engines(sigma: SigmaEngine, behavioral: BehavioralEngine) -> None:
    global _sigma_engine, _behavioral_engine
    _sigma_engine = sigma
    _behavioral_engine = behavioral


async def process_raw_event(source: str, raw: dict) -> NormalizedEvent:
    """Full pipeline for a single raw Kafka event."""
    event = normalize(source, raw)
    event = enrich(event)

    doc_id: str | None = None
    try:
        doc_id = await index_event(event)
    except Exception as exc:
        logger.error("index_event_failed", source=source, error=str(exc))

    if _sigma_engine is None or _behavioral_engine is None:
        logger.warning("detection_engines_not_initialized")
        return event

    sigma_hits = _sigma_engine.evaluate(event)
    behavioral_hits = await _behavioral_engine.evaluate(event)

    for detection in sigma_hits + behavioral_hits:
        try:
            alert = await alert_service.create_from_detection(event, detection, doc_id)
            if alert:
                logger.debug("pipeline_alert", alert_id=alert.id, rule=detection.rule_id)
                # Tier 2: correlate the new alert into an incident.
                try:
                    await handle_new_alert(alert.id)
                except Exception as exc:
                    logger.error("correlation_failed", alert_id=alert.id, error=str(exc))
        except Exception as exc:
            logger.error("alert_creation_failed", rule=detection.rule_id, error=str(exc))

    return event
