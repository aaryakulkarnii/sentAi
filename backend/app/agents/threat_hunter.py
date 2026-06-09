"""Threat Hunter agent — gathers the incident's alerts and extracts entities."""

from __future__ import annotations

import structlog
from sqlalchemy import select

from app.agents.state import InvestigationState
from app.db.postgres import AsyncSessionLocal
from app.models.alert import Alert
from app.models.incident import Incident, IncidentAlert

logger = structlog.get_logger(__name__)


async def threat_hunter_node(state: InvestigationState) -> InvestigationState:
    incident_id = state["incident_id"]
    async with AsyncSessionLocal() as db:
        incident = await db.get(Incident, incident_id)
        if incident is None:
            state["alerts"] = []
            return state

        alerts = (
            await db.execute(
                select(Alert)
                .join(IncidentAlert, IncidentAlert.alert_id == Alert.id)
                .where(IncidentAlert.incident_id == incident_id)
                .order_by(Alert.created_at.asc())
            )
        ).scalars().all()

        state["incident"] = {
            "id": incident.id,
            "title": incident.title,
            "status": incident.status,
            "risk_score": incident.risk_score,
        }
        state["risk_score"] = incident.risk_score
        state["alerts"] = [
            {
                "id": a.id,
                "severity": a.severity,
                "confidence": a.confidence,
                "source_ip": a.source_ip,
                "dest_ip": a.dest_ip,
                "description": a.description,
                "mitre_technique_id": a.mitre_technique_id,
                "created_at": a.created_at.isoformat(),
            }
            for a in alerts
        ]

    ips = sorted({a["source_ip"] for a in state["alerts"] if a["source_ip"]})
    techniques = sorted({a["mitre_technique_id"] for a in state["alerts"] if a["mitre_technique_id"]})
    state["entities"] = {"ips": ips, "techniques": techniques}
    state.setdefault("agent_log", []).append(
        {"agent": "threat_hunter", "summary": f"Collected {len(state['alerts'])} alerts, {len(ips)} source IP(s)."}
    )
    logger.info("threat_hunter_done", incident_id=incident_id, alerts=len(state["alerts"]))
    return state
