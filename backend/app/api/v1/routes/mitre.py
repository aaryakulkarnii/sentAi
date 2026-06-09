"""MITRE ATT&CK endpoints."""

from fastapi import APIRouter, Depends
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.postgres import get_db
from app.models.mitre import MitreTechnique

router = APIRouter()


@router.get("/techniques")
async def list_techniques(db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(MitreTechnique))
    return result.scalars().all()


@router.get("/techniques/{technique_id}")
async def get_technique(technique_id: str, db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(MitreTechnique).where(MitreTechnique.id == technique_id))
    t = result.scalar_one_or_none()
    if not t:
        from fastapi import HTTPException
        raise HTTPException(404, "Technique not found")
    return t
