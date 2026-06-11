"""PostgreSQL log indexing with JSONB."""

from __future__ import annotations

from datetime import datetime, timezone
import structlog
import uuid

from app.ingestion.schema import NormalizedEvent
from app.db.postgres import AsyncSessionLocal
from app.models.log_event import LogEvent

logger = structlog.get_logger(__name__)


def _event_document(event: NormalizedEvent) -> dict:
    return {
        "@timestamp": event.timestamp.astimezone(timezone.utc).isoformat(),
        "source_type": event.source_type,
        "event_type": event.event_type,
        "severity": event.severity,
        "user": event.user,
        "host": event.host,
        "source_ip": event.source_ip,
        "dest_ip": event.dest_ip,
        "source_port": event.source_port,
        "dest_port": event.dest_port,
        "process_name": event.process_name,
        "process_id": event.process_id,
        "command_line": event.command_line,
        "file_path": event.file_path,
        "network_protocol": event.network_protocol,
        "geo_country": event.geo_country,
        "geo_city": event.geo_city,
        "asn": event.asn,
        "schema_version": event.schema_version,
        "raw": event.raw,
    }


async def ensure_index_templates() -> None:
    # No-op since we use Postgres instead of OpenSearch templates
    pass


async def index_event(event: NormalizedEvent) -> str | None:
    """Index a normalised event into PostgreSQL LogEvents."""
    doc = _event_document(event)
    event_id = str(uuid.uuid4())
    
    async with AsyncSessionLocal() as session:
        log_event = LogEvent(
            id=event_id,
            timestamp=event.timestamp,
            source_type=event.source_type,
            event_type=event.event_type,
            severity=event.severity,
            source_ip=event.source_ip,
            dest_ip=event.dest_ip,
            data=doc
        )
        session.add(log_event)
        try:
            await session.commit()
            return event_id
        except Exception as exc:
            logger.error("postgres_index_event_failed", error=str(exc))
            return None


async def index_alert_document(alert_data: dict) -> None:
    """Alert metadata is already stored in Postgres via the Alert model."""
    pass

