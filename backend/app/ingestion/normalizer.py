"""Translate raw source-specific events into NormalizedEvent."""

from datetime import UTC, datetime

from app.ingestion.schema import NormalizedEvent


def _parse_ts(raw: dict) -> datetime:
    ts = raw.get("@timestamp") or raw.get("eventTime") or raw.get("timestamp")
    if ts:
        if isinstance(ts, str):
            return datetime.fromisoformat(ts.replace("Z", "+00:00"))
        if isinstance(ts, (int, float)):
            return datetime.fromtimestamp(ts, tz=UTC)
    return datetime.now(UTC)


def normalize_sysmon(raw: dict) -> NormalizedEvent:
    source = raw.get("source") or {}
    return NormalizedEvent(
        timestamp=_parse_ts(raw),
        event_type=str(raw.get("winlog", {}).get("event_id", "unknown")),
        host=(raw.get("host") or {}).get("name"),
        user=(raw.get("user") or {}).get("name"),
        source_ip=source.get("ip") if isinstance(source, dict) else raw.get("source_ip"),
        process_name=(raw.get("process") or {}).get("name"),
        process_id=(raw.get("process") or {}).get("pid"),
        command_line=(raw.get("process") or {}).get("command_line"),
        source_type="sysmon",
        raw=raw,
    )


def normalize_auditd(raw: dict) -> NormalizedEvent:
    auditd = raw.get("auditd") or {}
    return NormalizedEvent(
        timestamp=_parse_ts(raw),
        event_type=auditd.get("message_type") or raw.get("event_type", "unknown"),
        host=(raw.get("host") or {}).get("name"),
        user=(raw.get("user") or {}).get("name"),
        source_ip=raw.get("source", {}).get("ip") if isinstance(raw.get("source"), dict) else raw.get("src_ip"),
        source_type="auditd",
        raw=raw,
    )


def normalize_cloudtrail(raw: dict) -> NormalizedEvent:
    user_identity = raw.get("userIdentity") or {}
    return NormalizedEvent(
        timestamp=_parse_ts(raw),
        event_type=raw.get("eventName", "unknown"),
        user=user_identity.get("userName") or user_identity.get("arn"),
        source_ip=raw.get("sourceIPAddress"),
        source_type="cloudtrail",
        raw=raw,
    )


def normalize_network(raw: dict) -> NormalizedEvent:
    return NormalizedEvent(
        timestamp=_parse_ts(raw),
        event_type=raw.get("action") or raw.get("event_type", "network"),
        host=raw.get("hostname") or raw.get("device_name"),
        source_ip=raw.get("src_ip") or raw.get("source_ip"),
        dest_ip=raw.get("dst_ip") or raw.get("dest_ip") or raw.get("destination_ip"),
        source_port=_to_int(raw.get("src_port") or raw.get("source_port")),
        dest_port=_to_int(raw.get("dst_port") or raw.get("dest_port") or raw.get("destination_port")),
        network_protocol=raw.get("protocol"),
        bytes_sent=_to_int(raw.get("bytes_sent")),
        source_type="network",
        raw=raw,
    )


def _to_int(value) -> int | None:
    if value is None:
        return None
    try:
        return int(value)
    except (TypeError, ValueError):
        return None


NORMALIZERS = {
    "sysmon": normalize_sysmon,
    "auditd": normalize_auditd,
    "cloudtrail": normalize_cloudtrail,
    "network": normalize_network,
}


def normalize(source_type: str, raw: dict) -> NormalizedEvent:
    fn = NORMALIZERS.get(source_type)
    if fn:
        return fn(raw)
    return NormalizedEvent(
        timestamp=_parse_ts(raw),
        event_type="unknown",
        source_type=source_type,
        raw=raw,
    )
