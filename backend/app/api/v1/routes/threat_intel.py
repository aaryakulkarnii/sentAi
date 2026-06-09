"""Threat intelligence query endpoints."""

from fastapi import APIRouter, Query

router = APIRouter()


@router.get("/ioc/search")
async def search_ioc(q: str = Query(..., description="IP, hash, or domain to query")):
    # TODO: fan out to AbuseIPDB, OTX, MalwareBazaar
    return {"query": q, "results": []}


@router.get("/cve/{cve_id}")
async def get_cve(cve_id: str):
    # TODO: query NVD API
    return {"cve_id": cve_id}
