"""Threat Intelligence agent — enriches source IPs and collects IOCs."""

from __future__ import annotations

import structlog

from app.agents.state import InvestigationState
from app.services.threat_intel.connectors import search_ioc

logger = structlog.get_logger(__name__)


async def intel_node(state: InvestigationState) -> InvestigationState:
    ips = state.get("entities", {}).get("ips", [])[:5]
    intel: dict[str, dict] = {}
    iocs: list[dict] = []

    for ip in ips:
        try:
            result = await search_ioc(ip)
        except Exception as exc:
            logger.warning("intel_lookup_failed", ip=ip, error=str(exc))
            result = {"ioc": ip, "type": "ip", "verdict": "unknown", "sources": []}
        intel[ip] = result
        iocs.append({"value": ip, "type": "ip", "verdict": result.get("verdict", "unknown")})

    state["threat_intel"] = intel
    state["iocs"] = iocs
    malicious = sum(1 for i in iocs if i["verdict"] in ("malicious", "suspicious"))
    state.setdefault("agent_log", []).append(
        {"agent": "intel", "summary": f"Enriched {len(iocs)} IOC(s); {malicious} flagged."}
    )
    logger.info("intel_done", iocs=len(iocs), flagged=malicious)
    return state
