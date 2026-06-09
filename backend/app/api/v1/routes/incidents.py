"""Incident management endpoints."""

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.postgres import get_db
from app.models.incident import Incident, IncidentAlert, IncidentNote
from app.schemas.incident import IncidentCreate, IncidentNoteCreate, IncidentResponse, IncidentUpdate

router = APIRouter()


@router.get("/", response_model=list[IncidentResponse])
async def list_incidents(db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(Incident).order_by(Incident.created_at.desc()))
    return result.scalars().all()


@router.post("/", response_model=IncidentResponse, status_code=201)
async def create_incident(body: IncidentCreate, db: AsyncSession = Depends(get_db)):
    incident = Incident(title=body.title, description=body.description)
    db.add(incident)
    await db.flush()
    for alert_id in body.alert_ids:
        db.add(IncidentAlert(incident_id=incident.id, alert_id=alert_id))
    await db.commit()
    await db.refresh(incident)
    return incident


@router.get("/{incident_id}", response_model=IncidentResponse)
async def get_incident(incident_id: str, db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(Incident).where(Incident.id == incident_id))
    inc = result.scalar_one_or_none()
    if not inc:
        raise HTTPException(404, "Incident not found")
    return inc


@router.patch("/{incident_id}", response_model=IncidentResponse)
async def update_incident(incident_id: str, body: IncidentUpdate, db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(Incident).where(Incident.id == incident_id))
    inc = result.scalar_one_or_none()
    if not inc:
        raise HTTPException(404, "Incident not found")
    for field, value in body.model_dump(exclude_none=True).items():
        setattr(inc, field, value)
    await db.commit()
    await db.refresh(inc)
    return inc


@router.post("/{incident_id}/notes", status_code=201)
async def add_note(incident_id: str, body: IncidentNoteCreate, db: AsyncSession = Depends(get_db)):
    note = IncidentNote(incident_id=incident_id, author_id="system", content=body.content)
    db.add(note)
    await db.commit()
    return {"status": "ok"}
