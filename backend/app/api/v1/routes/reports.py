"""Report generation endpoints."""

import os
from fastapi import APIRouter, Depends, HTTPException
from fastapi.responses import FileResponse
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.deps import get_current_user
from app.db.postgres import get_db
from app.models.report import Report
from app.models.incident import Incident, IncidentAlert
from app.models.alert import Alert
from app.models.user import User
from app.schemas.report import ReportResponse
from app.services.reporting import generate_pdf_report, generate_docx_report

router = APIRouter()

REPORTS_DIR = os.path.join(os.getcwd(), "data", "reports")


@router.get("/", response_model=list[ReportResponse])
async def list_reports(
    db: AsyncSession = Depends(get_db),
    _: User = Depends(get_current_user),
):
    q = select(Report).order_by(Report.created_at.desc())
    return list((await db.execute(q)).scalars().all())


@router.post("/generate/{incident_id}", response_model=ReportResponse)
async def generate_report(
    incident_id: str,
    format: str = "pdf",
    db: AsyncSession = Depends(get_db),
    user: User = Depends(get_current_user),
):
    if format not in ("pdf", "docx"):
        raise HTTPException(400, "Format must be pdf or docx")

    # Fetch incident
    inc = await db.get(Incident, incident_id)
    if not inc:
        raise HTTPException(404, "Incident not found")

    # Fetch alerts
    q = (
        select(Alert)
        .join(IncidentAlert, IncidentAlert.alert_id == Alert.id)
        .where(IncidentAlert.incident_id == incident_id)
        .order_by(Alert.created_at.asc())
    )
    alerts = list((await db.execute(q)).scalars().all())

    # Create report record
    report = Report(incident_id=incident_id, format=format, created_by=user.id)
    db.add(report)
    await db.flush()  # to get report.id

    filename = f"report_{report.id}.{format}"
    file_path = os.path.join(REPORTS_DIR, filename)

    try:
        if format == "pdf":
            generate_pdf_report(inc, alerts, file_path)
        else:
            generate_docx_report(inc, alerts, file_path)
    except Exception as e:
        raise HTTPException(500, f"Report generation failed: {str(e)}")

    report.s3_key = file_path
    await db.commit()
    await db.refresh(report)

    return report


@router.get("/{report_id}/download")
async def download_report(
    report_id: str,
    db: AsyncSession = Depends(get_db),
    _: User = Depends(get_current_user),
):
    report = await db.get(Report, report_id)
    if not report:
        raise HTTPException(404, "Report not found")
    
    if not report.s3_key or not os.path.exists(report.s3_key):
        raise HTTPException(404, "Report file not found on disk")
        
    return FileResponse(
        report.s3_key,
        media_type="application/pdf" if report.format == "pdf" else "application/vnd.openxmlformats-officedocument.wordprocessingml.document",
        filename=os.path.basename(report.s3_key)
    )
