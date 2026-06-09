"""OpenSearch log indexing with daily indices and index templates."""

from __future__ import annotations

from datetime import datetime, timezone

import structlog

from app.db.opensearch import ALERTS_INDEX, get_opensearch, log_index
from app.ingestion.schema import NormalizedEvent

logger = structlog.get_logger(__name__)

LOG_TEMPLATE = "sentinelai-logs-template"
LOG_INDEX_PATTERN = "logs-*"


def _index_name(event: NormalizedEvent) -> str:
    date = event.timestamp.astimezone(timezone.utc).strftime("%Y.%m.%d")
    return log_index(event.source_type, date)


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
    client = get_opensearch()

    log_template = {
        "index_patterns": [LOG_INDEX_PATTERN],
        "template": {
            "settings": {"number_of_shards": 1, "number_of_replicas": 0},
            "mappings": {
                "properties": {
                    "@timestamp": {"type": "date"},
                    "source_type": {"type": "keyword"},
                    "event_type": {"type": "keyword"},
                    "severity": {"type": "keyword"},
                    "user": {"type": "keyword"},
                    "host": {"type": "keyword"},
                    "source_ip": {"type": "ip"},
                    "dest_ip": {"type": "ip"},
                    "source_port": {"type": "integer"},
                    "dest_port": {"type": "integer"},
                    "process_name": {"type": "keyword"},
                    "command_line": {"type": "text"},
                    "geo_country": {"type": "keyword"},
                    "geo_city": {"type": "keyword"},
                    "asn": {"type": "keyword"},
                    "raw": {"type": "object", "enabled": False},
                }
            },
        },
    }

    alerts_template = {
        "index_patterns": [ALERTS_INDEX],
        "template": {
            "settings": {"number_of_shards": 1, "number_of_replicas": 0},
            "mappings": {
                "properties": {
                    "@timestamp": {"type": "date"},
                    "alert_id": {"type": "keyword"},
                    "severity": {"type": "keyword"},
                    "confidence": {"type": "float"},
                    "source_ip": {"type": "ip"},
                    "dest_ip": {"type": "ip"},
                    "description": {"type": "text"},
                    "rule_id": {"type": "keyword"},
                    "mitre_technique_id": {"type": "keyword"},
                    "status": {"type": "keyword"},
                }
            },
        },
    }

    for name, body in [(LOG_TEMPLATE, log_template), ("sentinelai-alerts-template", alerts_template)]:
        try:
            await client.indices.put_index_template(name=name, body=body)
            logger.info("index_template_created", name=name)
        except Exception as exc:
            logger.warning("index_template_error", name=name, error=str(exc))


async def index_event(event: NormalizedEvent) -> str:
    """Index a normalised event; returns the OpenSearch document ID."""
    client = get_opensearch()
    index = _index_name(event)
    doc = _event_document(event)
    resp = await client.index(index=index, body=doc, refresh=False)
    return resp["_id"]


async def index_alert_document(alert_data: dict) -> None:
    """Index alert metadata for search."""
    client = get_opensearch()
    doc = {
        "@timestamp": datetime.now(timezone.utc).isoformat(),
        **alert_data,
    }
    await client.index(index=ALERTS_INDEX, body=doc, refresh=False)
