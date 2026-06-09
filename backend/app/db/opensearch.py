"""OpenSearch async client."""

from opensearchpy import AsyncOpenSearch

from app.core.config import settings

_client: AsyncOpenSearch | None = None


async def init_opensearch() -> None:
    global _client
    _client = AsyncOpenSearch(
        hosts=[{"host": settings.OPENSEARCH_HOST, "port": settings.OPENSEARCH_PORT}],
        use_ssl=False,
    )


def get_opensearch() -> AsyncOpenSearch:
    if _client is None:
        raise RuntimeError("OpenSearch not initialised")
    return _client


# Index name helpers
def log_index(source: str, date: str) -> str:
    return f"logs-{source}-{date}"


ALERTS_INDEX = "sentinelai-alerts"
