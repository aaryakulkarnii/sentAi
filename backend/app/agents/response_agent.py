"""Response agent node – generates remediation plan."""

from app.agents.graph import InvestigationState


async def response_node(state: InvestigationState) -> InvestigationState:
    # TODO: produce step-by-step remediation recommendations
    return state
