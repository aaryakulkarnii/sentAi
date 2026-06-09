"""RAG retrieval from Qdrant."""

from app.db.qdrant import COLLECTION_THREAT, get_qdrant
from app.rag.embedder import embed


async def retrieve(query: str, top_k: int = 5) -> list[dict]:
    client = get_qdrant()
    vectors = embed([query])
    results = await client.search(
        collection_name=COLLECTION_THREAT,
        query_vector=vectors[0],
        limit=top_k,
        with_payload=True,
    )
    return [{"score": r.score, **r.payload} for r in results]
