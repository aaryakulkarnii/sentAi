"""Qdrant vector store client (optional — disabled in DEV_MODE)."""

from __future__ import annotations

from typing import Any

from app.core.config import settings

_client: Any | None = None

COLLECTION_THREAT = "threat_knowledge"
COLLECTION_IOC = "ioc_embeddings"
VECTOR_DIM = 768


async def init_qdrant() -> None:
    """Connect to Qdrant and ensure collections. No-op in DEV_MODE."""
    global _client
    if settings.DEV_MODE:
        return
    from qdrant_client import AsyncQdrantClient
    from qdrant_client.models import Distance, VectorParams

    _client = AsyncQdrantClient(host=settings.QDRANT_HOST, port=settings.QDRANT_PORT)
    for name in (COLLECTION_THREAT, COLLECTION_IOC):
        collections = await _client.get_collections()
        existing = [c.name for c in collections.collections]
        if name not in existing:
            await _client.create_collection(
                name, vectors_config=VectorParams(size=VECTOR_DIM, distance=Distance.COSINE)
            )


def get_qdrant():
    """Return the client, or None when Qdrant is disabled/unavailable."""
    return _client
