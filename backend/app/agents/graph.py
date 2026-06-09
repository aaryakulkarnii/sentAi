"""Investigation orchestrator.

Runs the six agent nodes sequentially (no LangGraph dependency) and persists the
result to the investigations table with status tracking.
"""

from __future__ import annotations

import uuid
from datetime import datetime, timezone

import structlog

from app.agents.executive_agent import executive_node
from app.agents.intel_agent import intel_node
from app.agents.investigation_agent import investigation_node
from app.agents.mitre_agent import mitre_node
from app.agents.response_agent import response_node
from app.agents.state import InvestigationState
from app.agents.threat_hunter import threat_hunter_node
from app.db.postgres import AsyncSessionLocal
from app.models.investigation import Investigation

logger = structlog.get_logger(__name__)

PIPELINE = [
    ("threat_hunter", threat_hunter_node),
    ("intel", intel_node),
    ("mitre", mitre_node),
    ("investigator", investigation_node),
    ("response", response_node),
    ("executive", executive_node),
]


async def _save(incident_id: str, status: str, state: InvestigationState | None) -> str:
    """Upsert the latest investigation row for an incident."""
    async with AsyncSessionLocal() as db:
        inv = Investigation(
            id=str(uuid.uuid4()),
            incident_id=incident_id,
            status=status,
            risk_score=(state or {}).get("risk_score", 0),
            agent_output={"log": (state or {}).get("agent_log", []),
                          "entities": (state or {}).get("entities", {}),
                          "incident": (state or {}).get("incident", {})},
            attack_timeline={"events": (state or {}).get("attack_timeline", [])},
            mitre_mappings=(state or {}).get("mitre_mappings", {}),
            iocs={"items": (state or {}).get("iocs", []),
                  "threat_intel": (state or {}).get("threat_intel", {})},
            remediation={**(state or {}).get("remediation", {}),
                         "executive_summary": (state or {}).get("executive_summary", "")},
            created_at=datetime.now(timezone.utc),
        )
        db.add(inv)
        await db.commit()
        return inv.id


async def run_investigation(incident_id: str) -> dict:
    logger.info("investigation_started", incident_id=incident_id)
    state: InvestigationState = {"incident_id": incident_id, "agent_log": []}

    try:
        for name, node in PIPELINE:
            state = await node(state)
    except Exception as exc:
        logger.error("investigation_failed", incident_id=incident_id, error=str(exc))
        await _save(incident_id, "failed", state)
        raise

    inv_id = await _save(incident_id, "complete", state)
    logger.info(
        "investigation_complete",
        incident_id=incident_id,
        investigation_id=inv_id,
        risk_score=state.get("risk_score", 0),
    )
    return {"investigation_id": inv_id, **state}
