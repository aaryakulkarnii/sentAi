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

engine = create_async_engine(settings.DATABASE_URL, **_engine_kwargs)
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
            await conn.run_sync(Base.metadata.create_all)
        logger.info("dev_db_ready", url=settings.DATABASE_URL)
        return

    async with engine.connect() as conn:
        await conn.execute(text("SELECT 1"))


async def get_db():
    async with AsyncSessionLocal() as session:
        yield session
