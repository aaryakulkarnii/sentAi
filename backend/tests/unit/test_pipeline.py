"""Integration tests for the event processing pipeline."""

from unittest.mock import AsyncMock, MagicMock, patch

import pytest

from app.ingestion.pipeline import init_engines, process_raw_event
from app.services.detection.behavioral import BehavioralEngine
from app.services.detection.sigma_engine import DetectionResult, SigmaEngine


@pytest.fixture
def mock_engines():
    sigma = MagicMock(spec=SigmaEngine)
    sigma.evaluate.return_value = [
        DetectionResult(
            rule_id="test-rule",
            rule_name="Test Mimikatz Execution",
            severity="critical",
            confidence=0.9,
            mitre_technique_id=None,
        )
    ]
    behavioral = AsyncMock(spec=BehavioralEngine)
    behavioral.evaluate.return_value = []
    init_engines(sigma, behavioral)
    return sigma, behavioral


@pytest.mark.asyncio
async def test_pipeline_creates_alert(mock_engines):
    raw = {
        "@timestamp": "2024-06-01T12:00:00Z",
        "winlog": {"event_id": 1},
        "host": {"name": "ws-alice"},
        "process": {"name": "mimikatz.exe", "command_line": "mimikatz"},
    }

    with (
        patch("app.ingestion.pipeline.index_event", AsyncMock(return_value="doc-123")),
        patch("app.ingestion.pipeline.enrich", side_effect=lambda e: e),
        patch("app.ingestion.pipeline.alert_service.create_from_detection", AsyncMock()) as mock_alert,
    ):
        await process_raw_event("sysmon", raw)

    mock_alert.assert_called_once()
    sigma, _ = mock_engines
    sigma.evaluate.assert_called_once()
