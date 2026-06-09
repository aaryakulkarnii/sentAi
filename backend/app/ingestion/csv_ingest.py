"""CSV log ingestion — the headline 'upload your logs' path.

Parses an uploaded CSV of security events, maps columns flexibly to the unified
NormalizedEvent schema, and runs each row through the detection → correlation
pipeline. No Kafka required.
"""

from __future__ import annotations

import csv
import io
from datetime import UTC, datetime

import structlog

from app.ingestion.pipeline import process_event
from app.ingestion.schema import NormalizedEvent

logger = structlog.get_logger(__name__)

# Accepted column aliases (lower-cased) → normalized field.
FIELD_ALIASES = {
    "timestamp": ["timestamp", "@timestamp", "time", "datetime", "date", "event_time", "eventtime"],
    "source_ip": ["source_ip", "src_ip", "sourceip", "srcip", "ip", "client_ip", "source", "saddr"],
    "dest_ip": ["dest_ip", "dst_ip", "destination_ip", "destip", "dstip", "daddr"],
    "source_port": ["source_port", "src_port", "srcport", "sport"],
    "dest_port": ["dest_port", "dst_port", "destination_port", "dstport", "port", "dport"],
    "user": ["user", "username", "user_name", "account", "acct", "src_user"],
    "host": ["host", "hostname", "computer", "device", "device_name", "dest_host", "machine"],
    "event_type": ["event_type", "eventid", "event_id", "action", "message_type", "activity",
                   "event", "signature", "type"],
    "process_name": ["process_name", "process", "image", "proc", "process_image"],
    "command_line": ["command_line", "commandline", "cmd", "command", "args"],
    "severity": ["severity", "level", "priority"],
    "network_protocol": ["protocol", "proto", "network_protocol"],
    "outcome": ["outcome", "result", "status", "auth_result"],
    "source_type": ["source_type", "log_type", "product", "log_source", "vendor"],
}

FAILED_TOKENS = {"fail", "failed", "failure", "denied", "deny", "blocked", "invalid", "error"}


def _build_index(headers: list[str]) -> dict[str, str]:
    """Map normalized field → actual header name present in the CSV."""
    lower = {h.lower().strip(): h for h in headers}
    index: dict[str, str] = {}
    for field, aliases in FIELD_ALIASES.items():
        for alias in aliases:
            if alias in lower:
                index[field] = lower[alias]
                break
    return index


def _to_int(value: str | None) -> int | None:
    if not value:
        return None
    try:
        return int(float(value))
    except (TypeError, ValueError):
        return None


def _parse_ts(value: str | None) -> datetime:
    if value:
        for fmt in (None,):  # try ISO first
            try:
                return datetime.fromisoformat(value.replace("Z", "+00:00"))
            except ValueError:
                pass
        for fmt in ("%Y-%m-%d %H:%M:%S", "%m/%d/%Y %H:%M:%S", "%Y/%m/%d %H:%M:%S"):
            try:
                return datetime.strptime(value, fmt).replace(tzinfo=UTC)
            except ValueError:
                continue
    return datetime.now(UTC)


def _infer_source_type(event: NormalizedEvent, explicit: str | None) -> str:
    if explicit:
        return explicit.lower()
    if event.dest_port is not None or event.network_protocol:
        return "network"
    if event.process_name or event.command_line:
        return "sysmon"
    return "csv"


def row_to_event(row: dict[str, str], index: dict[str, str]) -> NormalizedEvent:
    def get(field: str) -> str | None:
        col = index.get(field)
        val = row.get(col) if col else None
        return val.strip() if isinstance(val, str) and val.strip() else None

    outcome = (get("outcome") or "").lower()
    event_type = get("event_type") or "log"
    # Normalise failed-auth signals so the behavioral engine fires.
    if any(tok in outcome for tok in FAILED_TOKENS) or any(
        tok in event_type.lower() for tok in FAILED_TOKENS
    ):
        event_type = "login_failed"

    event = NormalizedEvent(
        timestamp=_parse_ts(get("timestamp")),
        event_type=event_type,
        severity=(get("severity") or "info").lower(),
        user=get("user"),
        host=get("host"),
        source_ip=get("source_ip"),
        dest_ip=get("dest_ip"),
        source_port=_to_int(get("source_port")),
        dest_port=_to_int(get("dest_port")),
        process_name=get("process_name"),
        command_line=get("command_line"),
        network_protocol=get("network_protocol"),
        source_type="csv",
        raw={**row, "outcome": outcome or None},
    )
    event.source_type = _infer_source_type(event, get("source_type"))
    return event


async def ingest_csv(content: bytes, max_rows: int = 50_000) -> dict:
    text = content.decode("utf-8-sig", errors="replace")
    reader = csv.DictReader(io.StringIO(text))
    headers = reader.fieldnames or []
    if not headers:
        return {"rows": 0, "alerts": 0, "error": "No CSV header row found."}

    index = _build_index(headers)
    if "source_ip" not in index and "host" not in index:
        return {
            "rows": 0, "alerts": 0,
            "error": "CSV needs at least a source IP or host column.",
            "detected_columns": list(index.keys()),
        }

    rows = 0
    alerts = 0
    for row in reader:
        if rows >= max_rows:
            break
        try:
            event = row_to_event(row, index)
            alerts += await process_event(event)
        except Exception as exc:
            logger.warning("csv_row_failed", error=str(exc))
        rows += 1

    logger.info("csv_ingested", rows=rows, alerts=alerts, columns=list(index.keys()))
    return {"rows": rows, "alerts": alerts, "detected_columns": list(index.keys())}


def sample_csv() -> str:
    """A demo CSV that triggers a multi-stage attack (port scan + brute force)."""
    lines = ["timestamp,source_ip,dest_ip,dest_port,user,host,action,protocol"]
    ts = "2026-06-09T10:00:00"
    attacker = "203.0.113.66"
    # Port scan: 25 ports.
    for p in range(1, 26):
        lines.append(f"{ts},{attacker},10.0.0.10,{p},,DC01,deny,tcp")
    # Brute force: 12 failed logins.
    for _ in range(12):
        lines.append(f"{ts},{attacker},10.0.0.10,,administrator,DC01,login_failed,")
    # Some benign traffic.
    for i in range(5):
        lines.append(f"{ts},10.0.2.{i + 30},10.0.0.10,443,alice,WS-DEV-12,allow,tcp")
    return "\n".join(lines) + "\n"
