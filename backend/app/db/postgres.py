"""Async SQLAlchemy engine and session factory."""

import structlog
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine
from sqlalchemy.orm import DeclarativeBase

from app.core.config import settings

logger = structlog.get_logger(__name__)

# SQLite (dev) doesn't support pool_pre_ping the same way; keep it simple.
_engine_kwargs = {"echo": False}
if not settings.DEV_MODE:
    _engine_kwargs["pool_pre_ping"] = True

engine = create_async_engine(settings.get_database_url, **_engine_kwargs)
AsyncSessionLocal = async_sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)


class Base(DeclarativeBase):
    pass


async def init_db() -> None:
    """Verify connectivity. In DEV_MODE, also create all tables (no Alembic)."""
    from sqlalchemy import text

    if settings.DEV_MODE:
        # Import models so they register on Base.metadata, then create tables.
        import app.models  # noqa: F401

        async with engine.begin() as conn:
            await conn.execute(text("CREATE EXTENSION IF NOT EXISTS vector;"))
            await conn.run_sync(Base.metadata.create_all)
        logger.info("dev_db_ready", url=settings.get_database_url)
        return

    async with engine.begin() as conn:
        await conn.execute(text("CREATE EXTENSION IF NOT EXISTS vector;"))
        await conn.execute(text("SELECT 1"))
        await conn.run_sync(Base.metadata.create_all)
        
    async with AsyncSessionLocal() as session:
        await seed_vector_db_if_empty(session)


async def get_db():
    async with AsyncSessionLocal() as session:
        yield session

async def seed_vector_db_if_empty(session: AsyncSession) -> None:
    from sqlalchemy import select
    from app.models.knowledge import ThreatKnowledge
    from app.data.mitre_seed import seed_records
    from app.data.playbooks import PLAYBOOKS
    from app.rag.embedder import embed

    result = await session.execute(select(ThreatKnowledge).limit(1))
    if result.scalars().first():
        return

    logger.info("seeding_pgvector_threat_knowledge")
    try:
        docs = []
        for rec in seed_records():
            mitigation = rec.get("mitigation", {}).get("summary", "")
            text = f"{rec['technique']} ({rec['id']}). {rec['description']} Mitigation: {mitigation}"
            title = f"{rec['id']} {rec['technique']}"
            vectors = embed([text])
            docs.append(
                ThreatKnowledge(
                    external_id=rec["id"],
                    title=title,
                    text=text,
                    source="mitre",
                    embedding=vectors[0]
                )
            )

        for tid, pb in PLAYBOOKS.items():
            text = f"{pb['title']}. Response: " + " ".join(pb["steps"])
            vectors = embed([text])
            docs.append(
                ThreatKnowledge(
                    external_id=f"pb-{tid}",
                    title=pb["title"],
                    text=text,
                    source="playbook",
                    embedding=vectors[0]
                )
            )

        if docs:
            session.add_all(docs)
            await session.commit()
            logger.info("pgvector_threat_knowledge_seeded", count=len(docs))
    except Exception as exc:
        logger.error("pgvector_seeding_failed", error=str(exc))
