"""Lightweight in-memory knowledge base for RAG grounding.

In production this would be Qdrant + sentence-transformers embeddings. In
DEV_MODE (zero-infra) we build a small corpus from the MITRE seed and playbooks
and retrieve by term-overlap scoring — instant, no model download, good enough
to ground the agents' prompts.
"""

from __future__ import annotations

import re
from dataclasses import dataclass, field

from app.data.mitre_seed import seed_records
from app.data.playbooks import PLAYBOOKS

_WORD = re.compile(r"[a-z0-9]+")

_STOP = frozenset(
    "the a an and or of to for in on with by from as is are be this that adversaries "
    "adversary use uses using via may can system systems data".split()
)


def _tokens(text: str) -> set[str]:
    return {w for w in _WORD.findall(text.lower()) if w not in _STOP and len(w) > 2}


@dataclass
class Document:
    id: str
    title: str
    text: str
    source: str
    tokens: set[str] = field(default_factory=set)


class KnowledgeBase:
    def __init__(self) -> None:
        self._docs: list[Document] = []
        self._built = False

    def build(self) -> None:
        if self._built:
            return
        for rec in seed_records():
            mitigation = rec.get("mitigation", {}).get("summary", "")
            text = f"{rec['technique']} ({rec['id']}). {rec['description']} Mitigation: {mitigation}"
            doc = Document(
                id=rec["id"],
                title=f"{rec['id']} {rec['technique']}",
                text=text,
                source="mitre",
            )
            doc.tokens = _tokens(text + " " + rec["tactic"])
            self._docs.append(doc)

        for tid, pb in PLAYBOOKS.items():
            text = f"{pb['title']}. Response: " + " ".join(pb["steps"])
            doc = Document(id=f"pb-{tid}", title=pb["title"], text=text, source="playbook")
            doc.tokens = _tokens(text)
            self._docs.append(doc)

        self._built = True

    def search(self, query: str, top_k: int = 4) -> list[Document]:
        self.build()
        q = _tokens(query)
        if not q:
            return []
        scored = [(len(q & d.tokens), d) for d in self._docs]
        scored = [(s, d) for s, d in scored if s > 0]
        scored.sort(key=lambda x: x[0], reverse=True)
        return [d for _, d in scored[:top_k]]

    def context_for(self, query: str, top_k: int = 4) -> str:
        """Return a compact context block for prompting."""
        docs = self.search(query, top_k)
        if not docs:
            return ""
        return "\n".join(f"- {d.title}: {d.text}" for d in docs)


knowledge_base = KnowledgeBase()
