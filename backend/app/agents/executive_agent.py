"""Executive agent node – produces management-ready summary."""

from app.agents.graph import InvestigationState


async def executive_node(state: InvestigationState) -> InvestigationState:
    # TODO: generate executive summary via LLM
    return state
