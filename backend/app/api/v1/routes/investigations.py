"""Investigation trigger, status, and retrieval endpoints (Tier 3)."""

import structlog
from fastapi import APIRouter, BackgroundTasks, Depends, HTTPException
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.deps import get_current_user
from app.db.postgres import get_db
from app.models.incident import Incident
from app.models.investigation import Investigation
from app.models.user import User
from app.schemas.investigation import (
    InvestigationResponse,
    InvestigationStatus,
    InvestigationTrigger,
)

logger = structlog.get_logger(__name__)
router = APIRouter()

# In-process status of in-flight investigations (incident_id -> status).
_running: dict[str, str] = {}


async def _run(incident_id: str) -> None:
    from app.agents.graph import run_investigation

    _running[incident_id] = "running"
    try:
        await run_investigation(incident_id)
        _running[incident_id] = "complete"
    except Exception as exc:
        logger.error("investigation_task_failed", incident_id=incident_id, error=str(exc))
        _running[incident_id] = "failed"


@router.post("/trigger", status_code=202)
async def trigger_investigation(
    body: InvestigationTrigger,
    background_tasks: BackgroundTasks,
    db: AsyncSession = Depends(get_db),
    _: User = Depends(get_current_user),
):
    incident = await db.get(Incident, body.incident_id)
    if not incident:
        raise HTTPException(404, "Incident not found")
    _running[body.incident_id] = "pending"
    background_tasks.add_task(_run, body.incident_id)
    return {"status": "queued", "incident_id": body.incident_id}


@router.get("/{incident_id}/status", response_model=InvestigationStatus)
async def investigation_status(
    incident_id: str,
    db: AsyncSession = Depends(get_db),
    _: User = Depends(get_current_user),
):
    in_flight = _running.get(incident_id)
    latest = (
        await db.execute(
            select(Investigation)
            .where(Investigation.incident_id == incident_id)
            .order_by(Investigation.created_at.desc())
            .limit(1)
        )
    ).scalar_one_or_none()

    if in_flight in ("pending", "running"):
        return InvestigationStatus(incident_id=incident_id, status=in_flight)
    if latest:
        return InvestigationStatus(
            incident_id=incident_id, status=latest.status, investigation_id=latest.id
        )
    return InvestigationStatus(incident_id=incident_id, status="none")


@router.get("/{incident_id}/latest", response_model=InvestigationResponse)
async def get_investigation(
    incident_id: str,
    db: AsyncSession = Depends(get_db),
    _: User = Depends(get_current_user),
):
    inv = (
        await db.execute(
            select(Investigation)
            .where(Investigation.incident_id == incident_id)
            .order_by(Investigation.created_at.desc())
            .limit(1)
        )
    ).scalar_one_or_none()
    if not inv:
        raise HTTPException(404, "No investigation found for this incident")
    return inv
