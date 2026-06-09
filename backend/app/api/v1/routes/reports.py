"""Report generation endpoints (Tier 4)."""

import uuid
from datetime import datetime, timezone

import structlog
from fastapi import APIRouter, Depends, HTTPException, Query
from fastapi.responses import Response
from pydantic import BaseModel
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.deps import get_current_user
from app.db.postgres import get_db
from app.models.report import Report
from app.models.user import User
from app.services.reporting.generator import gather_report_data, render
from app.services.reporting.storage import content_type, load_report, save_report

logger = structlog.get_logger(__name__)
router = APIRouter()

VALID_FORMATS = {"pdf", "docx"}


class ReportRequest(BaseModel):
    incident_id: str
    format: str = "pdf"


class ReportResponse(BaseModel):
    id: str
    incident_id: str
    format: str
    created_at: datetime

    model_config = {"from_attributes": True}


@router.post("/generate", response_model=ReportResponse, status_code=201)
async def generate_report(
    body: ReportRequest,
    db: AsyncSession = Depends(get_db),
    user: User = Depends(get_current_user),
):
    fmt = body.format.lower()
    if fmt not in VALID_FORMATS:
        raise HTTPException(422, "format must be 'pdf' or 'docx'")

    data = await gather_report_data(db, body.incident_id)
    if data is None:
        raise HTTPException(404, "Incident not found")

    report_id = str(uuid.uuid4())
    try:
        content = render(data, fmt)
        key = save_report(report_id, fmt, content)
    except Exception as exc:
        logger.error("report_generation_failed", error=str(exc))
        raise HTTPException(500, f"Report generation failed: {exc}")

    report = Report(
        id=report_id, incident_id=body.incident_id, format=fmt,
        s3_key=key, created_by=user.id, created_at=datetime.now(timezone.utc),
    )
    db.add(report)
    await db.commit()
    await db.refresh(report)
    logger.info("report_generated", report_id=report_id, format=fmt)
    return report


@router.get("/", response_model=list[ReportResponse])
async def list_reports(
    incident_id: str | None = Query(None),
    db: AsyncSession = Depends(get_db),
    _: User = Depends(get_current_user),
):
    q = select(Report).order_by(Report.created_at.desc())
    if incident_id:
        q = q.where(Report.incident_id == incident_id)
    return list((await db.execute(q)).scalars().all())


@router.get("/{report_id}/download")
async def download_report(
    report_id: str,
    db: AsyncSession = Depends(get_db),
    _: User = Depends(get_current_user),
):
    report = await db.get(Report, report_id)
    if not report or not report.s3_key:
        raise HTTPException(404, "Report not found")
    try:
        content = load_report(report.s3_key)
    except Exception as exc:
        raise HTTPException(404, f"Report file unavailable: {exc}")
    filename = f"sentinelai_report_{report_id[:8]}.{report.format}"
    return Response(
        content=content,
        media_type=content_type(report.format),
        headers={"Content-Disposition": f"attachment; filename={filename}"},
    )
