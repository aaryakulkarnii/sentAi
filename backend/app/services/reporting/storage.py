"""Report storage — local filesystem in DEV_MODE, S3 in production."""

from __future__ import annotations

from pathlib import Path

import structlog

from app.core.config import settings

logger = structlog.get_logger(__name__)

REPORTS_DIR = Path("reports")

CONTENT_TYPES = {
    "pdf": "application/pdf",
    "docx": "application/vnd.openxmlformats-officedocument.wordprocessingml.document",
}


def content_type(fmt: str) -> str:
    return CONTENT_TYPES.get(fmt, "application/octet-stream")


def save_report(report_id: str, fmt: str, content: bytes) -> str:
    """Persist report bytes. Returns a storage key (local path or S3 key)."""
    key = f"reports/{report_id}.{fmt}"
    if settings.DEV_MODE:
        REPORTS_DIR.mkdir(parents=True, exist_ok=True)
        path = REPORTS_DIR / f"{report_id}.{fmt}"
        path.write_bytes(content)
        return str(path)

    import boto3

    s3 = boto3.client("s3", region_name=settings.AWS_REGION)
    s3.put_object(
        Bucket=settings.S3_BUCKET_REPORTS, Key=key, Body=content,
        ContentType=content_type(fmt),
    )
    return key


def load_report(key: str) -> bytes:
    if settings.DEV_MODE:
        return Path(key).read_bytes()

    import boto3

    s3 = boto3.client("s3", region_name=settings.AWS_REGION)
    obj = s3.get_object(Bucket=settings.S3_BUCKET_REPORTS, Key=key)
    return obj["Body"].read()
