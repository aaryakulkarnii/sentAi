"""Qdrant vector store client."""

from qdrant_client import AsyncQdrantClient
from qdrant_client.models import Distance, VectorParams

from app.core.config import settings

_client: AsyncQdrantClient | None = None

COLLECTION_THREAT = "threat_knowledge"
COLLECTION_IOC = "ioc_embeddings"
VECTOR_DIM = 768


async def init_qdrant() -> None:
    global _client
    _client = AsyncQdrantClient(host=settings.QDRANT_HOST, port=settings.QDRANT_PORT)
    for name in (COLLECTION_THREAT, COLLECTION_IOC):
        collections = await _client.get_collections()
        existing = [c.name for c in collections.collections]
        if name not in existing:
            await _client.create_collection(
                name, vectors_config=VectorParams(size=VECTOR_DIM, distance=Distance.COSINE)
            )


def get_qdrant() -> AsyncQdrantClient:
    if _client is None:
        raise RuntimeError("Qdrant not initialised")
    return _client
