"""Response agent — synthesises remediation steps from playbooks + LLM."""

from __future__ import annotations

import structlog

from app.agents.state import InvestigationState
from app.data.playbooks import playbook_for
from app.rag.knowledge import knowledge_base
from app.services.llm import llm

logger = structlog.get_logger(__name__)


async def response_node(state: InvestigationState) -> InvestigationState:
    techniques = state.get("entities", {}).get("techniques", [])
    primary = techniques[0] if techniques else None

    # Base playbook(s) from the knowledge base.
    playbooks = []
    seen_titles = set()
    for tid in techniques or [None]:
        pb = playbook_for(tid)
        if pb["title"] not in seen_titles:
            playbooks.append(pb)
            seen_titles.add(pb["title"])

    base_steps: list[str] = []
    for pb in playbooks:
        base_steps.extend(pb["steps"])

    immediate = base_steps[:3]
    follow_up = base_steps[3:8]

    # Optional LLM refinement grounded in the playbook context.
    llm_steps = None
    if llm.available and techniques:
        ctx = knowledge_base.context_for(" ".join(techniques), top_k=3)
        prompt = (
            f"An incident involves MITRE techniques {', '.join(techniques)}.\n"
            f"Context:\n{ctx}\n\n"
            "List 4-6 concise, prioritized remediation steps a SOC analyst should take. "
            "Return one step per line, no numbering."
        )
        text = await llm.complete(prompt, max_tokens=400)
        if text:
            llm_steps = [s.strip("-• ").strip() for s in text.splitlines() if s.strip()][:6]

    state["remediation"] = {
        "primary_technique": primary,
        "playbooks": [pb["title"] for pb in playbooks],
        "immediate_actions": immediate,
        "follow_up_actions": follow_up,
        "ai_recommended": llm_steps,
        "source": "llm+playbook" if llm_steps else "playbook",
    }
    state.setdefault("agent_log", []).append(
        {"agent": "response", "summary": f"Generated remediation from {len(playbooks)} playbook(s)."}
    )
    logger.info("response_done", playbooks=len(playbooks), llm=bool(llm_steps))
    return state
