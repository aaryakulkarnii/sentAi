"""Map NormalizedEvent to Sigma-compatible field dictionaries."""

from __future__ import annotations

from typing import Any

from app.ingestion.schema import NormalizedEvent

# Sigma field aliases → flattened event keys (checked in order)
FIELD_ALIASES: dict[str, list[str]] = {
    "Image": ["process.executable", "process.name", "process.image", "Image"],
    "CommandLine": ["process.command_line", "CommandLine"],
    "EventID": ["winlog.event_id", "event.code", "EventID"],
    "User": ["user.name", "User", "user"],
    "SourceIp": ["source.ip", "source_ip", "SourceIp"],
    "DestinationIp": ["destination.ip", "dest_ip", "DestinationIp"],
    "DestinationPort": ["destination.port", "dest_port", "DestinationPort"],
    "SourcePort": ["source.port", "source_port", "SourcePort"],
    "HostName": ["host.name", "host", "HostName"],
    "EventName": ["event.action", "eventName", "EventName"],
    "Action": ["event.action", "action", "Action"],
    "Outcome": ["event.outcome", "outcome", "Outcome"],
}


def _flatten(data: dict[str, Any], parent: str = "", sep: str = ".") -> dict[str, Any]:
    flat: dict[str, Any] = {}
    for key, value in data.items():
        full = f"{parent}{sep}{key}" if parent else key
        if isinstance(value, dict):
            flat.update(_flatten(value, full, sep))
        else:
            flat[full] = value
    return flat


def event_to_fields(event: NormalizedEvent) -> dict[str, Any]:
    """Build a flat field dict for Sigma rule matching."""
    fields: dict[str, Any] = _flatten(event.raw)

    # Normalized top-level fields
    fields.update(
        {
            "source_type": event.source_type,
            "event_type": str(event.event_type),
            "severity": event.severity,
            "host.name": event.host,
            "user.name": event.user,
            "source.ip": event.source_ip,
            "destination.ip": event.dest_ip,
            "process.name": event.process_name,
            "process.command_line": event.command_line,
            "destination.port": event.dest_port,
            "source.port": event.source_port,
            "file.path": event.file_path,
            "network.protocol": event.network_protocol,
        }
    )

    # Sigma shorthand keys
    if event.process_name:
        fields["Image"] = event.process_name
    if event.command_line:
        fields["CommandLine"] = event.command_line
    if event.host:
        fields["HostName"] = event.host
    if event.source_ip:
        fields["SourceIp"] = event.source_ip
    if event.dest_ip:
        fields["DestinationIp"] = event.dest_ip
    if event.dest_port is not None:
        fields["DestinationPort"] = event.dest_port
    if event.user:
        fields["User"] = event.user

    return {k: v for k, v in fields.items() if v is not None}


def resolve_field(fields: dict[str, Any], sigma_field: str) -> Any:
    """Resolve a Sigma field name to a value from the event field dict."""
    if sigma_field in fields:
        return fields[sigma_field]

    for alias in FIELD_ALIASES.get(sigma_field, []):
        if alias in fields:
            return fields[alias]

    # Dot-path fallback
    if sigma_field in fields:
        return fields[sigma_field]

    return None
