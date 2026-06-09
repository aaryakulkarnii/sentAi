"""Investigation agent node – builds attack timeline."""

from app.agents.graph import InvestigationState


async def investigation_node(state: InvestigationState) -> InvestigationState:
    # TODO: construct ordered attack chain from events
    return state
