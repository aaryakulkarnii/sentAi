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
    await seed_qdrant_if_empty(_client)


async def seed_qdrant_if_empty(client) -> None:
    """If COLLECTION_THREAT is empty, load MITRE and playbook data and upload embeddings."""
    try:
        count_res = await client.count(collection_name=COLLECTION_THREAT, exact=True)
        if count_res.count > 0:
            return
    except Exception as exc:
        logger.warning("qdrant_count_failed", error=str(exc))
        return

    logger.info("seeding_qdrant_threat_knowledge")
    try:
        from app.data.mitre_seed import seed_records
        from app.data.playbooks import PLAYBOOKS
        from app.rag.embedder import embed
        from qdrant_client.models import PointStruct

        points = []
        point_idx = 1

        # Load MITRE
        for rec in seed_records():
            mitigation = rec.get("mitigation", {}).get("summary", "")
            text = f"{rec['technique']} ({rec['id']}). {rec['description']} Mitigation: {mitigation}"
            title = f"{rec['id']} {rec['technique']}"
            payload = {
                "id": rec["id"],
                "title": title,
                "text": text,
                "source": "mitre",
            }
            vectors = embed([text])
            points.append(PointStruct(id=point_idx, vector=vectors[0], payload=payload))
            point_idx += 1

        # Load Playbooks
        for tid, pb in PLAYBOOKS.items():
            text = f"{pb['title']}. Response: " + " ".join(pb["steps"])
            payload = {
                "id": f"pb-{tid}",
                "title": pb["title"],
                "text": text,
                "source": "playbook",
            }
            vectors = embed([text])
            points.append(PointStruct(id=point_idx, vector=vectors[0], payload=payload))
            point_idx += 1

        if points:
            await client.upsert(collection_name=COLLECTION_THREAT, points=points)
            logger.info("qdrant_threat_knowledge_seeded", count=len(points))
    except Exception as exc:
        logger.error("qdrant_seeding_failed", error=str(exc))


def get_qdrant():
    """Return the client, or None when Qdrant is disabled/unavailable."""
    return _client
