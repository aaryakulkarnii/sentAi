"""Tests for extended normalizers."""

from app.ingestion.normalizer import normalize


def test_cloudtrail_normalizer():
    raw = {
        "eventTime": "2024-06-01T12:00:00Z",
        "eventName": "ConsoleLogin",
        "sourceIPAddress": "203.0.113.1",
        "userIdentity": {"userName": "alice"},
    }
    event = normalize("cloudtrail", raw)
    assert event.source_type == "cloudtrail"
    assert event.event_type == "ConsoleLogin"
    assert event.source_ip == "203.0.113.1"
    assert event.user == "alice"


def test_network_normalizer():
    raw = {
        "@timestamp": "2024-06-01T12:00:00Z",
        "src_ip": "10.0.0.1",
        "dst_ip": "10.0.0.50",
        "dst_port": 443,
        "action": "deny",
    }
    event = normalize("network", raw)
    assert event.source_type == "network"
    assert event.source_ip == "10.0.0.1"
    assert event.dest_port == 443
