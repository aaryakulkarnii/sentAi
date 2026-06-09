"""SentinelAI – FastAPI application entry point."""

from contextlib import asynccontextmanager

import structlog
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.api.v1 import router as api_v1_router
from app.api.ws.alerts import router as ws_alerts_router
from app.core.config import settings
from app.core.events import on_shutdown, on_startup
from app.core.logging import configure_logging

configure_logging()
logger = structlog.get_logger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    await on_startup()
    yield
    await on_shutdown()


app = FastAPI(
    title="SentinelAI",
    description="Autonomous AI-powered SOC platform",
    version="0.1.0",
    docs_url="/docs",
    redoc_url="/redoc",
    lifespan=lifespan,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.ALLOWED_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(api_v1_router, prefix="/api/v1")
app.include_router(ws_alerts_router, prefix="/ws")


@app.get("/health")
async def health_check():
    from app.services.health import run_health_checks

    return await run_health_checks()
