"""Investigation trigger and retrieval endpoints."""

from fastapi import APIRouter, BackgroundTasks, Depends, HTTPException
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.postgres import get_db
from app.models.investigation import Investigation
from app.schemas.investigation import InvestigationResponse, InvestigationTrigger

router = APIRouter()


@router.post("/trigger", status_code=202)
async def trigger_investigation(
    body: InvestigationTrigger,
    background_tasks: BackgroundTasks,
    db: AsyncSession = Depends(get_db),
):
    from app.agents.graph import run_investigation
    background_tasks.add_task(run_investigation, body.incident_id)
    return {"status": "queued", "incident_id": body.incident_id}


@router.get("/{incident_id}/latest", response_model=InvestigationResponse)
async def get_investigation(incident_id: str, db: AsyncSession = Depends(get_db)):
    result = await db.execute(
        select(Investigation)
        .where(Investigation.incident_id == incident_id)
        .order_by(Investigation.created_at.desc())
        .limit(1)
    )
    inv = result.scalar_one_or_none()
    if not inv:
        raise HTTPException(404, "No investigation found for this incident")
    return inv
