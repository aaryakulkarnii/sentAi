"""MITRE ATT&CK agent — maps techniques via Postgres lookup + RAG context."""

from __future__ import annotations

import structlog

from app.agents.state import InvestigationState
from app.db.postgres import AsyncSessionLocal
from app.models.mitre import MitreTechnique
from app.rag.knowledge import knowledge_base

logger = structlog.get_logger(__name__)


async def mitre_node(state: InvestigationState) -> InvestigationState:
    techniques = state.get("entities", {}).get("techniques", [])
    mappings: dict[str, dict] = {}

    async with AsyncSessionLocal() as db:
        for tid in techniques:
            row = await db.get(MitreTechnique, tid)
            if row:
                mappings[tid] = {
                    "id": row.id,
                    "tactic": row.tactic,
                    "technique": row.technique,
                    "sub_technique": row.sub_technique,
                    "description": row.description,
                    "mitigation": row.mitigation.get("summary") if row.mitigation else None,
                    "url": row.url,
                }
            else:
                ctx = await knowledge_base.search(tid, top_k=1)
                mappings[tid] = {
                    "id": tid,
                    "technique": ctx[0].title if ctx else tid,
                    "description": ctx[0].text if ctx else None,
                }

    state["mitre_mappings"] = mappings
    tactics = sorted({m.get("tactic") for m in mappings.values() if m.get("tactic")})
    state.setdefault("agent_log", []).append(
        {"agent": "mitre", "summary": f"Mapped {len(mappings)} technique(s) across {len(tactics)} tactic(s)."}
    )
    logger.info("mitre_done", techniques=len(mappings))
    return state
