"""OpenSearch async client (optional — disabled in DEV_MODE)."""

from __future__ import annotations

from typing import Any

from app.core.config import settings

_client: Any | None = None


async def init_opensearch() -> None:
    """Connect to OpenSearch. No-op in DEV_MODE (search indexing disabled)."""
    global _client
    if settings.DEV_MODE:
        return
    from opensearchpy import AsyncOpenSearch

    _client = AsyncOpenSearch(
        hosts=[{"host": settings.OPENSEARCH_HOST, "port": settings.OPENSEARCH_PORT}],
        use_ssl=False,
    )


def get_opensearch():
    """Return the client, or None when OpenSearch is disabled/unavailable."""
    return _client


# Index name helpers
def log_index(source: str, date: str) -> str:
    return f"logs-{source}-{date}"


ALERTS_INDEX = "sentinelai-alerts"
