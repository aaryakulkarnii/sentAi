"""RAG retrieval from Qdrant."""

from sqlalchemy import select
from app.db.postgres import AsyncSessionLocal
from app.rag.embedder import embed
from app.models.knowledge import ThreatKnowledge

async def retrieve(query: str, top_k: int = 5) -> list[dict]:
    vectors = embed([query])
    query_vector = vectors[0]

    async with AsyncSessionLocal() as session:
        stmt = select(ThreatKnowledge).order_by(
            ThreatKnowledge.embedding.cosine_distance(query_vector)
        ).limit(top_k)
        
        result = await session.execute(stmt)
        records = result.scalars().all()
        
        return [
            {
                "id": r.external_id,
                "title": r.title,
                "text": r.text,
                "source": r.source,
                "score": 1.0  # Optional: compute 1 - cosine_distance if score is needed
            }
            for r in records
        ]
