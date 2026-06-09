"""Unit tests for dependency health checks."""

from unittest.mock import AsyncMock, MagicMock, patch

import pytest

from app.services.health import (
    check_kafka,
    check_opensearch,
    check_postgres,
    check_qdrant,
    check_redis,
    run_health_checks,
)


@pytest.mark.asyncio
async def test_check_postgres_ok():
    mock_engine = MagicMock()
    mock_conn = AsyncMock()
    mock_conn.execute = AsyncMock()
    mock_ctx = MagicMock()
    mock_ctx.__aenter__ = AsyncMock(return_value=mock_conn)
    mock_ctx.__aexit__ = AsyncMock(return_value=False)
    mock_engine.connect.return_value = mock_ctx

    with patch("app.services.health.engine", mock_engine):
        result = await check_postgres()
    assert result["status"] == "ok"


@pytest.mark.asyncio
async def test_check_redis_ok():
    mock_redis = AsyncMock()
    mock_redis.ping = AsyncMock(return_value=True)
    with patch("app.services.health.get_redis", return_value=mock_redis):
        result = await check_redis()
    assert result["status"] == "ok"


@pytest.mark.asyncio
async def test_check_opensearch_degraded_cluster():
    mock_client = AsyncMock()
    mock_client.cluster.health = AsyncMock(return_value={"status": "red"})
    with patch("app.services.health.get_opensearch", return_value=mock_client):
        result = await check_opensearch()
    assert result["status"] == "error"


@pytest.mark.asyncio
async def test_run_health_checks_all_ok():
    with (
        patch("app.services.health.check_postgres", AsyncMock(return_value={"status": "ok"})),
        patch("app.services.health.check_opensearch", AsyncMock(return_value={"status": "ok"})),
        patch("app.services.health.check_redis", AsyncMock(return_value={"status": "ok"})),
        patch("app.services.health.check_kafka", AsyncMock(return_value={"status": "ok"})),
        patch("app.services.health.check_qdrant", AsyncMock(return_value={"status": "ok"})),
    ):
        result = await run_health_checks()
    assert result["status"] == "ok"
    assert len(result["services"]) == 5


@pytest.mark.asyncio
async def test_check_kafka_ok():
    mock_admin = AsyncMock()
    mock_admin.start = AsyncMock()
    mock_admin.list_topics = AsyncMock(return_value=["sentinelai.sysmon"])
    mock_admin.close = AsyncMock()

    with patch("app.services.health.AIOKafkaAdminClient", return_value=mock_admin):
        result = await check_kafka()
    assert result["status"] == "ok"
    assert result["topics"] == 1


@pytest.mark.asyncio
async def test_check_qdrant_ok():
    mock_client = AsyncMock()
    collection = MagicMock()
    mock_client.get_collections = AsyncMock(
        return_value=MagicMock(collections=[collection, collection])
    )
    with patch("app.services.health.get_qdrant", return_value=mock_client):
        result = await check_qdrant()
    assert result["status"] == "ok"
    assert result["collections"] == 2
