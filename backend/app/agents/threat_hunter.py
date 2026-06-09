"""Threat hunter agent node – finds suspicious activity in alerts."""

from app.agents.graph import InvestigationState


async def threat_hunter_node(state: InvestigationState) -> InvestigationState:
    # TODO: query OpenSearch for events related to incident_id
    return state
