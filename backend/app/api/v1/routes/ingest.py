"""Log ingestion endpoints — CSV upload (Tier 3 headline feature)."""

from fastapi import APIRouter, Depends, File, HTTPException, UploadFile
from fastapi.responses import PlainTextResponse

from app.api.deps import get_current_user
from app.ingestion.csv_ingest import ingest_csv, sample_csv
from app.models.user import User

router = APIRouter()

MAX_BYTES = 25 * 1024 * 1024  # 25 MB


@router.post("/csv")
async def upload_csv(
    file: UploadFile = File(...),
    _: User = Depends(get_current_user),
):
    if not (file.filename or "").lower().endswith(".csv"):
        raise HTTPException(400, "Please upload a .csv file.")
    content = await file.read()
    if len(content) > MAX_BYTES:
        raise HTTPException(413, "File too large (max 25 MB).")
    result = await ingest_csv(content)
    if result.get("error"):
        raise HTTPException(422, result["error"])
    return {"filename": file.filename, **result}


@router.get("/sample", response_class=PlainTextResponse)
async def download_sample(_: User = Depends(get_current_user)):
    return PlainTextResponse(
        sample_csv(),
        headers={"Content-Disposition": "attachment; filename=sentinelai_sample_logs.csv"},
    )
