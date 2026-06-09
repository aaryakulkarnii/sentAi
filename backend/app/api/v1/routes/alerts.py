"""Alert management endpoints."""

from fastapi import APIRouter, Depends, Query
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.postgres import get_db
from app.models.alert import Alert
from app.schemas.alert import AlertResponse, AlertUpdate

router = APIRouter()


@router.get("/", response_model=list[AlertResponse])
async def list_alerts(
    severity: str | None = Query(None),
    status: str | None = Query(None),
    limit: int = Query(50, le=500),
    offset: int = 0,
    db: AsyncSession = Depends(get_db),
):
    q = select(Alert).order_by(Alert.created_at.desc()).limit(limit).offset(offset)
    if severity:
        q = q.where(Alert.severity == severity)
    if status:
        q = q.where(Alert.status == status)
    result = await db.execute(q)
    return result.scalars().all()


@router.get("/{alert_id}", response_model=AlertResponse)
async def get_alert(alert_id: str, db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(Alert).where(Alert.id == alert_id))
    alert = result.scalar_one_or_none()
    if not alert:
        from fastapi import HTTPException
        raise HTTPException(404, "Alert not found")
    return alert


@router.patch("/{alert_id}", response_model=AlertResponse)
async def update_alert(alert_id: str, body: AlertUpdate, db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(Alert).where(Alert.id == alert_id))
    alert = result.scalar_one_or_none()
    if not alert:
        from fastapi import HTTPException
        raise HTTPException(404, "Alert not found")
    if body.status:
        alert.status = body.status
    await db.commit()
    return alert
