"""Executive agent — produces a management-ready summary via LLM (or template)."""

from __future__ import annotations

import structlog

from app.agents.state import InvestigationState
from app.services.llm import llm

logger = structlog.get_logger(__name__)


def _risk_label(score: int) -> str:
    if score >= 80:
        return "Critical"
    if score >= 60:
        return "High"
    if score >= 40:
        return "Medium"
    return "Low"


def _template_summary(state: InvestigationState) -> str:
    incident = state.get("incident", {})
    alerts = state.get("alerts", [])
    ips = state.get("entities", {}).get("ips", [])
    techniques = state.get("entities", {}).get("techniques", [])
    tactics = sorted({m.get("tactic") for m in state.get("mitre_mappings", {}).values() if m.get("tactic")})
    flagged = [i for i in state.get("iocs", []) if i.get("verdict") in ("malicious", "suspicious")]
    score = state.get("risk_score", 0)

    parts = [
        f"Incident \"{incident.get('title', 'Unknown')}\" was assessed at {_risk_label(score)} "
        f"risk (score {score}/100).",
        f"It correlates {len(alerts)} alert(s) "
        + (f"originating from {', '.join(ips)}. " if ips else "with no single source. "),
    ]
    if techniques:
        parts.append(
            f"Observed attacker techniques span {len(techniques)} ATT&CK technique(s) "
            f"({', '.join(techniques)})"
            + (f" across tactics: {', '.join(tactics)}. " if tactics else ". ")
        )
    if flagged:
        parts.append(f"{len(flagged)} indicator(s) were flagged by threat intelligence. ")
    parts.append(
        "Recommended next steps: contain the affected entities, reset exposed credentials, "
        "and follow the attached remediation playbook."
    )
    return " ".join(parts)


async def executive_node(state: InvestigationState) -> InvestigationState:
    summary = None
    if llm.available:
        incident = state.get("incident", {})
        facts = {
            "title": incident.get("title"),
            "risk_score": state.get("risk_score"),
            "alerts": len(state.get("alerts", [])),
            "source_ips": state.get("entities", {}).get("ips", []),
            "techniques": state.get("entities", {}).get("techniques", []),
            "timeline_steps": len(state.get("attack_timeline", [])),
            "flagged_iocs": [i for i in state.get("iocs", []) if i.get("verdict") != "clean"],
        }
        prompt = (
            "Write a concise 3-4 sentence executive summary of this security incident for "
            f"non-technical leadership. Facts (JSON):\n{facts}\n"
            "State the risk level, what happened, the attacker behaviour, and the recommended action."
        )
        summary = await llm.complete(prompt, max_tokens=350)

    state["executive_summary"] = summary or _template_summary(state)
    state.setdefault("agent_log", []).append(
        {"agent": "executive", "summary": "Produced executive summary.",
         "via": "llm" if summary else "template"}
    )
    logger.info("executive_done", via="llm" if summary else "template")
    return state
