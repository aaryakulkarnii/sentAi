"""Report generation endpoints."""

from fastapi import APIRouter, BackgroundTasks

router = APIRouter()


@router.post("/generate/{incident_id}")
async def generate_report(incident_id: str, format: str = "pdf", background_tasks: BackgroundTasks = None):
    # TODO: invoke reporting service
    return {"status": "queued", "incident_id": incident_id, "format": format}
