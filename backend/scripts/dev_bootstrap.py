"""Seed the zero-infra dev database (SQLite).

Creates tables and seeds: a dev/admin user (matching the frontend mock identity),
a couple of demo analysts, sample assets, and the curated MITRE technique set.

Run from the backend/ directory:  python -m scripts.dev_bootstrap
"""

import asyncio

import structlog
from sqlalchemy import select

from app.api.deps import DEV_USER_EMAIL, DEV_USER_ID, DEV_USER_ROLE
from app.core.security import hash_password
from app.data.mitre_seed import seed_records
from app.db.postgres import AsyncSessionLocal, init_db
from app.models.asset import Asset
from app.models.mitre import MitreTechnique
from app.models.user import User

logger = structlog.get_logger(__name__)

USERS = [
    (DEV_USER_ID, DEV_USER_EMAIL, DEV_USER_ROLE, "password"),
    ("00000000-0000-0000-0000-000000000002", "tier1@sentinelai.dev", "tier1", "password"),
    ("00000000-0000-0000-0000-000000000003", "tier2@sentinelai.dev", "tier2", "password"),
    ("00000000-0000-0000-0000-000000000004", "engineer@sentinelai.dev", "engineer", "password"),
]

ASSETS = [
    ("DC01", "10.0.0.10", "Windows Server 2022", 5, "Identity Team"),
    ("WEB01", "10.0.1.20", "Ubuntu 22.04", 4, "Platform Team"),
    ("WS-FINANCE-07", "10.0.2.45", "Windows 11", 4, "Finance"),
    ("JUMP01", "10.0.0.5", "Windows Server 2019", 5, "Infra Team"),
    ("WS-DEV-12", "10.0.3.88", "Windows 11", 2, "Engineering"),
]


async def seed_users(db) -> int:
    n = 0
    for uid, email, role, pw in USERS:
        existing = await db.get(User, uid)
        if existing:
            continue
        db.add(User(id=uid, email=email, role=role, password_hash=hash_password(pw)))
        n += 1
    return n


async def seed_assets(db) -> int:
    n = 0
    for hostname, ip, os_name, crit, owner in ASSETS:
        exists = (
            await db.execute(select(Asset).where(Asset.hostname == hostname))
        ).scalar_one_or_none()
        if exists:
            continue
        db.add(Asset(hostname=hostname, ip=ip, os=os_name, criticality=crit, owner=owner))
        n += 1
    return n


async def seed_mitre(db) -> int:
    n = 0
    for rec in seed_records():
        existing = await db.get(MitreTechnique, rec["id"])
        if existing:
            continue
        db.add(MitreTechnique(**rec))
        n += 1
    return n


async def main() -> None:
    await init_db()  # DEV_MODE: also creates all tables
    async with AsyncSessionLocal() as db:
        users = await seed_users(db)
        assets = await seed_assets(db)
        mitre = await seed_mitre(db)
        await db.commit()
    print(f"[ok] Seeded: {users} users, {assets} assets, {mitre} MITRE techniques")
    print(f"     Login: {DEV_USER_EMAIL} / password  (role: {DEV_USER_ROLE})")


if __name__ == "__main__":
    asyncio.run(main())
