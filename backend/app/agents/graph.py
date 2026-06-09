"""LangGraph investigation workflow."""

from typing import TypedDict

import structlog
from langgraph.graph import END, StateGraph

from app.agents.executive_agent import executive_node
from app.agents.intel_agent import intel_node
from app.agents.investigation_agent import investigation_node
from app.agents.mitre_agent import mitre_node
from app.agents.response_agent import response_node
from app.agents.threat_hunter import threat_hunter_node

logger = structlog.get_logger(__name__)


class InvestigationState(TypedDict):
    incident_id: str
    alerts: list[dict]
    suspicious_events: list[dict]
    threat_intel: dict
    mitre_mappings: dict
    attack_timeline: list[dict]
    iocs: list[str]
    remediation: dict
    executive_summary: str
    risk_score: int


def build_graph() -> StateGraph:
    g = StateGraph(InvestigationState)
    g.add_node("threat_hunter", threat_hunter_node)
    g.add_node("intel", intel_node)
    g.add_node("mitre", mitre_node)
    g.add_node("investigator", investigation_node)
    g.add_node("response", response_node)
    g.add_node("executive", executive_node)

    g.set_entry_point("threat_hunter")
    g.add_edge("threat_hunter", "intel")
    g.add_edge("intel", "mitre")
    g.add_edge("mitre", "investigator")
    g.add_edge("investigator", "response")
    g.add_edge("response", "executive")
    g.add_edge("executive", END)
    return g


_graph = build_graph().compile()


async def run_investigation(incident_id: str) -> dict:
    logger.info("investigation_started", incident_id=incident_id)
    initial: InvestigationState = {
        "incident_id": incident_id,
        "alerts": [],
        "suspicious_events": [],
        "threat_intel": {},
        "mitre_mappings": {},
        "attack_timeline": [],
        "iocs": [],
        "remediation": {},
        "executive_summary": "",
        "risk_score": 0,
    }
    result = await _graph.ainvoke(initial)
    logger.info("investigation_complete", incident_id=incident_id, risk_score=result["risk_score"])
    return result
