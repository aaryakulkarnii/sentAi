"""System configuration / status endpoint (Tier 4 — Settings page)."""

from fastapi import APIRouter, Depends

from app.api.deps import get_current_user
from app.core.config import settings
from app.models.user import User

router = APIRouter()


@router.get("/config")
async def system_config(_: User = Depends(get_current_user)):
    """Non-secret configuration status for the Settings UI."""
    return {
        "mode": "dev" if settings.DEV_MODE else "production",
        "version": "0.1.0",
        "llm": {
            "provider": "Groq",
            "model": settings.GROQ_MODEL,
            "configured": bool(settings.GROQ_API_KEY),
        },
        "threat_intel": {
            "abuseipdb": bool(settings.ABUSEIPDB_API_KEY),
            "otx": bool(settings.OTX_API_KEY),
            "malwarebazaar": True,  # no key required
            "nvd": True,  # no key required
        },
        "storage": {
            "reports": "local" if settings.DEV_MODE else "s3",
        },
        "detection": {
            "brute_force_threshold": settings.BEHAVIORAL_BRUTE_FORCE_THRESHOLD,
            "port_scan_threshold": settings.BEHAVIORAL_PORT_SCAN_THRESHOLD,
            "correlation_window_s": settings.CORRELATION_WINDOW,
        },
    }
