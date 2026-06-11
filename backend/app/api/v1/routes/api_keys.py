import hashlib
import secrets
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.deps import get_current_user
from app.db.postgres import get_db
from app.models.api_key import ApiKey
from app.models.user import User
from app.schemas.api_key import ApiKeyCreate, ApiKeyResponse, ApiKeyCreateResponse

router = APIRouter()

def _generate_api_key() -> tuple[str, str, str]:
    """Generate a random API key, return (raw_key, prefix, hash)"""
    raw_key = "sk_sai_" + secrets.token_urlsafe(32)
    prefix = raw_key[:12]
    key_hash = hashlib.sha256(raw_key.encode()).hexdigest()
    return raw_key, prefix, key_hash

@router.get("/", response_model=list[ApiKeyResponse])
async def list_api_keys(
    db: AsyncSession = Depends(get_db),
    user: User = Depends(get_current_user),
):
    q = select(ApiKey).where(ApiKey.user_id == user.id).order_by(ApiKey.created_at.desc())
    return list((await db.execute(q)).scalars().all())


@router.post("/", response_model=ApiKeyCreateResponse)
async def create_api_key(
    data: ApiKeyCreate,
    db: AsyncSession = Depends(get_db),
    user: User = Depends(get_current_user),
):
    raw_key, prefix, key_hash = _generate_api_key()
    
    api_key = ApiKey(
        name=data.name,
        prefix=prefix,
        key_hash=key_hash,
        user_id=user.id
    )
    db.add(api_key)
    await db.commit()
    await db.refresh(api_key)
    
    return ApiKeyCreateResponse(
        key=api_key,  # type: ignore
        secret_key=raw_key
    )

@router.delete("/{key_id}")
async def revoke_api_key(
    key_id: str,
    db: AsyncSession = Depends(get_db),
    user: User = Depends(get_current_user),
):
    key = await db.get(ApiKey, key_id)
    if not key or key.user_id != user.id:
        raise HTTPException(404, "API Key not found")
        
    key.is_active = False
    await db.commit()
    return {"status": "revoked"}
