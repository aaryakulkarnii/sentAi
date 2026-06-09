from fastapi import APIRouter

from app.api.v1.routes import (
    alerts,
    assets,
    auth,
    incidents,
    ingest,
    investigations,
    mitre,
    reports,
    system,
    threat_intel,
)

router = APIRouter()
router.include_router(auth.router,           prefix="/auth",           tags=["auth"])
router.include_router(alerts.router,         prefix="/alerts",         tags=["alerts"])
router.include_router(assets.router,         prefix="/assets",         tags=["assets"])
router.include_router(incidents.router,      prefix="/incidents",      tags=["incidents"])
router.include_router(ingest.router,         prefix="/ingest",         tags=["ingest"])
router.include_router(investigations.router, prefix="/investigations",  tags=["investigations"])
router.include_router(threat_intel.router,   prefix="/threat-intel",   tags=["threat-intel"])
router.include_router(mitre.router,          prefix="/mitre",          tags=["mitre"])
router.include_router(reports.router,        prefix="/reports",        tags=["reports"])
router.include_router(system.router,         prefix="/system",         tags=["system"])
