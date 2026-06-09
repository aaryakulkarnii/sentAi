"""FastAPI dependencies: authentication and role-based access control."""

from collections.abc import Iterable

from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.config import settings
from app.core.security import decode_token
from app.db.postgres import get_db
from app.models.user import User

# auto_error=False so DEV_MODE can fall back to a default analyst when no
# (or a mock) token is supplied by the frontend.
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/api/v1/auth/token", auto_error=False)

# Stable dev identity — matches the frontend MOCK_USER so FKs line up.
DEV_USER_ID = "00000000-0000-0000-0000-000000000001"
DEV_USER_EMAIL = "analyst@sentinelai.dev"
DEV_USER_ROLE = "manager"

# Simple role hierarchy: higher tiers inherit the privileges of lower ones.
ROLE_RANK = {"tier1": 1, "tier2": 2, "engineer": 3, "manager": 4}


def _dev_user() -> User:
    return User(id=DEV_USER_ID, email=DEV_USER_EMAIL, role=DEV_USER_ROLE, password_hash="")


async def get_current_user(
    token: str | None = Depends(oauth2_scheme),
    db: AsyncSession = Depends(get_db),
) -> User:
    # DEV_MODE: accept the frontend mock token (or none) and resolve a real
    # dev user if seeded, otherwise a transient one.
    if settings.DEV_MODE:
        if token:
            try:
                payload = decode_token(token)
                user_id = payload.get("sub")
                if user_id:
                    result = await db.execute(select(User).where(User.id == user_id))
                    user = result.scalar_one_or_none()
                    if user:
                        return user
            except ValueError:
                pass  # mock / invalid token — fall through to dev user
        seeded = await db.get(User, DEV_USER_ID)
        return seeded or _dev_user()

    if not token:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Not authenticated",
            headers={"WWW-Authenticate": "Bearer"},
        )
    try:
        payload = decode_token(token)
    except ValueError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or expired token",
            headers={"WWW-Authenticate": "Bearer"},
        )
    user_id = payload.get("sub")
    if not user_id:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid token payload")

    result = await db.execute(select(User).where(User.id == user_id))
    user = result.scalar_one_or_none()
    if not user:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="User not found")
    return user


def require_role(*roles: str):
    """Dependency factory enforcing that the user has one of `roles` (or higher).

    DEV_MODE is permissive — the structure exists for production but never
    blocks local work.
    """
    allowed: Iterable[str] = roles
    min_rank = min((ROLE_RANK.get(r, 99) for r in roles), default=99)

    async def _checker(user: User = Depends(get_current_user)) -> User:
        if settings.DEV_MODE:
            return user
        rank = ROLE_RANK.get(user.role, 0)
        if user.role in allowed or rank >= min_rank:
            return user
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail=f"Requires role: {' or '.join(roles)}",
        )

    return _checker
