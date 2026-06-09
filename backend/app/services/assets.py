"""Asset registry helpers — host/IP → asset resolution and criticality."""

from __future__ import annotations

from sqlalchemy import or_, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.asset import Asset

DEFAULT_CRITICALITY = 3


async def resolve_asset(
    db: AsyncSession, host: str | None, ip: str | None = None
) -> Asset | None:
    """Find the asset matching a hostname or IP (hostname takes priority)."""
    if not host and not ip:
        return None
    conds = []
    if host:
        conds.append(Asset.hostname == host)
    if ip:
        conds.append(Asset.ip == ip)
    result = await db.execute(select(Asset).where(or_(*conds)).limit(1))
    return result.scalar_one_or_none()


async def get_criticality(db: AsyncSession, host: str | None, ip: str | None = None) -> int:
    """Return the asset criticality (1–5) for a host/IP, defaulting to 3."""
    asset = await resolve_asset(db, host, ip)
    return asset.criticality if asset else DEFAULT_CRITICALITY
