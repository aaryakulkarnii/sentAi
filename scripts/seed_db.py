#!/usr/bin/env python3
"""Bootstrap the database with a default admin user."""

import asyncio
import sys; sys.path.insert(0, "backend")


async def main() -> None:
    from sqlalchemy import select

    from app.core.security import hash_password
    from app.db.postgres import AsyncSessionLocal, init_db
    from app.models.user import User

    await init_db()
    async with AsyncSessionLocal() as db:
        existing = await db.execute(select(User).where(User.email == "admin@sentinel.ai"))
        if existing.scalar_one_or_none():
            print("Admin user already exists: admin@sentinel.ai")
            return
        user = User(
            email="admin@sentinel.ai",
            password_hash=hash_password("changeme"),
            role="engineer",
        )
        db.add(user)
        await db.commit()
        print(f"Created admin user: {user.email}")


asyncio.run(main())
