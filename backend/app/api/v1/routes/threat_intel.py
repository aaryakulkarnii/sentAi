"""Threat intelligence query endpoints (Tier 3)."""

from fastapi import APIRouter, Depends, Query

from app.api.deps import get_current_user
from app.models.user import User
from app.services.threat_intel.connectors import search_ioc as _search_ioc

router = APIRouter()


@router.get("/ioc/search")
async def search_ioc(
    q: str = Query(..., description="IP, domain, hash, or CVE to query"),
    _: User = Depends(get_current_user),
):
    return await _search_ioc(q)


@router.get("/cve/{cve_id}")
async def get_cve(cve_id: str, _: User = Depends(get_current_user)):
    return await _search_ioc(cve_id)
