"""MITRE ATT&CK mapping agent node."""

from app.agents.graph import InvestigationState


async def mitre_node(state: InvestigationState) -> InvestigationState:
    # TODO: map suspicious events to ATT&CK techniques via RAG
    return state
