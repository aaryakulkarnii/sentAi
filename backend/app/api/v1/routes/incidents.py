"""Incident management endpoints (Tier 2 lifecycle)."""

from datetime import datetime, timezone

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.deps import get_current_user
from app.db.postgres import get_db
from app.models.alert import Alert
from app.models.incident import Incident, IncidentAlert, IncidentNote
from app.models.user import User
from app.schemas.alert import AlertResponse
from app.schemas.incident import (
    AssignUpdate,
    IncidentCreate,
    IncidentDetailResponse,
    IncidentNoteCreate,
    IncidentNoteResponse,
    IncidentResponse,
    StatusUpdate,
    TimelineEvent,
)
from app.services.correlation.engine import recompute_incident_risk

router = APIRouter()

# Allowed lifecycle transitions. "closed" is reachable from anywhere.
TRANSITIONS = {
    "open": {"investigating", "contained", "closed"},
    "investigating": {"contained", "resolved", "closed"},
    "contained": {"resolved", "investigating", "closed"},
    "resolved": {"closed", "investigating"},
    "closed": set(),
}
VALID_STATUSES = set(TRANSITIONS)


async def _get_or_404(db: AsyncSession, incident_id: str) -> Incident:
    inc = await db.get(Incident, incident_id)
    if not inc:
        raise HTTPException(404, "Incident not found")
    return inc


async def _member_alerts(db: AsyncSession, incident_id: str) -> list[Alert]:
    q = (
        select(Alert)
        .join(IncidentAlert, IncidentAlert.alert_id == Alert.id)
        .where(IncidentAlert.incident_id == incident_id)
        .order_by(Alert.created_at.asc())
    )
    return list((await db.execute(q)).scalars().all())


@router.get("/", response_model=list[IncidentResponse])
async def list_incidents(
    status: str | None = Query(None),
    db: AsyncSession = Depends(get_db),
    _: User = Depends(get_current_user),
):
    q = select(Incident).order_by(Incident.created_at.desc())
    if status:
        q = q.where(Incident.status == status)
    return list((await db.execute(q)).scalars().all())


@router.post("/", response_model=IncidentResponse, status_code=201)
async def create_incident(
    body: IncidentCreate,
    db: AsyncSession = Depends(get_db),
    user: User = Depends(get_current_user),
):
    incident = Incident(title=body.title, description=body.description, created_by=user.id)
    db.add(incident)
    await db.flush()
    for alert_id in body.alert_ids:
        db.add(IncidentAlert(incident_id=incident.id, alert_id=alert_id))
    await db.flush()
    await recompute_incident_risk(db, incident.id)
    await db.commit()
    await db.refresh(incident)
    return incident


@router.get("/{incident_id}", response_model=IncidentDetailResponse)
async def get_incident(
    incident_id: str,
    db: AsyncSession = Depends(get_db),
    _: User = Depends(get_current_user),
):
    inc = await _get_or_404(db, incident_id)
    alerts = await _member_alerts(db, incident_id)
    techniques = sorted({a.mitre_technique_id for a in alerts if a.mitre_technique_id})
    return IncidentDetailResponse(
        **IncidentResponse.model_validate(inc).model_dump(),
        alert_count=len(alerts),
        technique_ids=techniques,
    )


@router.patch("/{incident_id}", response_model=IncidentResponse)
async def update_incident(
    incident_id: str,
    body: StatusUpdate | AssignUpdate,
    db: AsyncSession = Depends(get_db),
    _: User = Depends(get_current_user),
):
    inc = await _get_or_404(db, incident_id)
    data = body.model_dump(exclude_none=True)
    if "status" in data:
        _apply_status(inc, data["status"])
    if "assigned_to" in data:
        inc.assigned_to = data["assigned_to"]
    inc.updated_at = datetime.now(timezone.utc)
    await db.commit()
    await db.refresh(inc)
    return inc


@router.post("/{incident_id}/status", response_model=IncidentResponse)
async def change_status(
    incident_id: str,
    body: StatusUpdate,
    db: AsyncSession = Depends(get_db),
    _: User = Depends(get_current_user),
):
    inc = await _get_or_404(db, incident_id)
    _apply_status(inc, body.status)
    inc.updated_at = datetime.now(timezone.utc)
    await db.commit()
    await db.refresh(inc)
    return inc


@router.post("/{incident_id}/assign", response_model=IncidentResponse)
async def assign_incident(
    incident_id: str,
    body: AssignUpdate,
    db: AsyncSession = Depends(get_db),
    _: User = Depends(get_current_user),
):
    inc = await _get_or_404(db, incident_id)
    inc.assigned_to = body.assigned_to
    inc.updated_at = datetime.now(timezone.utc)
    await db.commit()
    await db.refresh(inc)
    return inc


@router.post("/{incident_id}/escalate", response_model=IncidentResponse)
async def escalate_incident(
    incident_id: str,
    db: AsyncSession = Depends(get_db),
    user: User = Depends(get_current_user),
):
    inc = await _get_or_404(db, incident_id)
    if inc.status == "open":
        inc.status = "investigating"
    db.add(
        IncidentNote(
            incident_id=incident_id,
            author_id=user.id,
            content=f"Incident escalated by {user.email}.",
        )
    )
    inc.updated_at = datetime.now(timezone.utc)
    await db.commit()
    await db.refresh(inc)
    return inc


@router.get("/{incident_id}/alerts", response_model=list[AlertResponse])
async def incident_alerts(
    incident_id: str,
    db: AsyncSession = Depends(get_db),
    _: User = Depends(get_current_user),
):
    await _get_or_404(db, incident_id)
    return await _member_alerts(db, incident_id)


@router.get("/{incident_id}/timeline", response_model=list[TimelineEvent])
async def incident_timeline(
    incident_id: str,
    db: AsyncSession = Depends(get_db),
    _: User = Depends(get_current_user),
):
    await _get_or_404(db, incident_id)
    alerts = await _member_alerts(db, incident_id)
    return [
        TimelineEvent(
            timestamp=a.created_at,
            technique_id=a.mitre_technique_id,
            description=a.description,
            source_ip=a.source_ip,
            severity=a.severity,
        )
        for a in alerts
    ]


@router.get("/{incident_id}/notes", response_model=list[IncidentNoteResponse])
async def list_notes(
    incident_id: str,
    db: AsyncSession = Depends(get_db),
    _: User = Depends(get_current_user),
):
    await _get_or_404(db, incident_id)
    q = (
        select(IncidentNote)
        .where(IncidentNote.incident_id == incident_id)
        .order_by(IncidentNote.created_at.asc())
    )
    return list((await db.execute(q)).scalars().all())


@router.post("/{incident_id}/notes", response_model=IncidentNoteResponse, status_code=201)
async def add_note(
    incident_id: str,
    body: IncidentNoteCreate,
    db: AsyncSession = Depends(get_db),
    user: User = Depends(get_current_user),
):
    await _get_or_404(db, incident_id)
    note = IncidentNote(incident_id=incident_id, author_id=user.id, content=body.content)
    db.add(note)
    await db.commit()
    await db.refresh(note)
    return note


def _apply_status(inc: Incident, target: str) -> None:
    if target not in VALID_STATUSES:
        raise HTTPException(422, f"Invalid status '{target}'")
    if target == inc.status:
        return
    if target != "closed" and target not in TRANSITIONS.get(inc.status, set()):
        raise HTTPException(409, f"Cannot transition from '{inc.status}' to '{target}'")
    inc.status = target
