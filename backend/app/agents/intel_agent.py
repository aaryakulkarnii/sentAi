"""Threat intelligence agent node."""

from app.agents.graph import InvestigationState


async def intel_node(state: InvestigationState) -> InvestigationState:
    # TODO: enrich IOCs via AbuseIPDB, OTX, MalwareBazaar
    return state
