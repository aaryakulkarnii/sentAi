from datetime import UTC, datetime

from app.ingestion.normalizer import normalize


def test_sysmon_normalizer():
    raw = {
        "@timestamp": "2024-06-01T12:00:00",
        "winlog": {"event_id": 1},
        "host": {"name": "ws-alice"},
        "process": {"name": "cmd.exe", "pid": 1234, "command_line": "whoami"},
    }
    event = normalize("sysmon", raw)
    assert event.host == "ws-alice"
    assert event.process_name == "cmd.exe"
    assert event.source_type == "sysmon"


def test_unknown_source_fallback():
    raw = {"@timestamp": datetime.now(UTC).isoformat(), "foo": "bar"}
    event = normalize("unknown_source", raw)
    assert event.event_type == "unknown"
    assert event.source_type == "unknown_source"
