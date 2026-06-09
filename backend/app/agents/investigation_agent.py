"""Investigation agent — reconstructs the ordered attack timeline."""

from __future__ import annotations

import structlog

from app.agents.state import InvestigationState

logger = structlog.get_logger(__name__)


async def investigation_node(state: InvestigationState) -> InvestigationState:
    alerts = sorted(state.get("alerts", []), key=lambda a: a.get("created_at", ""))
    mappings = state.get("mitre_mappings", {})

    timeline: list[dict] = []
    for i, a in enumerate(alerts, start=1):
        tid = a.get("mitre_technique_id")
        mapping = mappings.get(tid, {}) if tid else {}
        timeline.append(
            {
                "step": i,
                "timestamp": a.get("created_at"),
                "technique_id": tid,
                "tactic": mapping.get("tactic"),
                "technique": mapping.get("technique"),
                "description": a.get("description"),
                "source_ip": a.get("source_ip"),
                "severity": a.get("severity"),
            }
        )

    state["attack_timeline"] = timeline
    state.setdefault("agent_log", []).append(
        {"agent": "investigator", "summary": f"Reconstructed a {len(timeline)}-step attack timeline."}
    )
    logger.info("investigation_done", steps=len(timeline))
    return state
