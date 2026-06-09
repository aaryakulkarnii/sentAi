"""Unified normalised event schema."""

from dataclasses import dataclass, field
from datetime import datetime


@dataclass
class NormalizedEvent:
    timestamp: datetime
    event_type: str
    severity: str = "info"
    user: str | None = None
    host: str | None = None
    source_ip: str | None = None
    dest_ip: str | None = None
    source_port: int | None = None
    dest_port: int | None = None
    process_name: str | None = None
    process_id: int | None = None
    command_line: str | None = None
    file_path: str | None = None
    network_protocol: str | None = None
    bytes_sent: int | None = None
    # Enrichment
    geo_country: str | None = None
    geo_city: str | None = None
    asn: str | None = None
    # Source tracking
    source_type: str = "unknown"
    raw: dict = field(default_factory=dict)
    schema_version: str = "1.0"
