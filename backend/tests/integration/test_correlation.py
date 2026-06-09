"""Tier 2 exit criterion: a multi-stage attack from one entity correlates into
a single incident with MITRE technique tags.

Runs fully in zero-infra mode (SQLite + in-memory Redis) — no Docker required.
Also runnable directly: `python -m tests.integration.test_correlation`.
"""

import time

from sqlalchemy import select

from app.core.config import settings
from app.db.postgres import AsyncSessionLocal, init_db
from app.db.redis import init_redis
from app.ingestion.pipeline import init_engines, process_raw_event
from app.models.alert import Alert
from app.models.incident import Incident, IncidentAlert
from app.services.detection.behavioral import BehavioralEngine
from app.services.detection.sigma_engine import SigmaEngine


async def _setup() -> None:
    assert settings.DEV_MODE, "test expects DEV_MODE"
    await init_db()
    await init_redis()
    init_engines(SigmaEngine(rules_dir=settings.SIGMA_RULES_DIR), BehavioralEngine())


def _unique_ip() -> str:
    n = time.time_ns()
    return f"198.51.{(n // 254) % 254 + 1}.{n % 254 + 1}"


async def _run_attack_chain(attacker_ip: str) -> None:
    # Stage 1 — port scan: 25 distinct destination ports (threshold 20 → T1046).
    for port in range(1, 26):
        await process_raw_event(
            "network",
            {"src_ip": attacker_ip, "dst_ip": "10.0.0.10", "dst_port": port,
             "protocol": "tcp", "action": "deny"},
        )

    # Stage 2 — brute force: 12 failed auths (threshold 10 → T1110).
    for _ in range(12):
        await process_raw_event(
            "auditd",
            {"auditd": {"message_type": "login_failed"}, "src_ip": attacker_ip,
             "user": {"name": "administrator"}, "host": {"name": "DC01"}, "outcome": "failure"},
        )


async def _assert_single_incident(attacker_ip: str) -> dict:
    async with AsyncSessionLocal() as db:
        alert_ids = (
            await db.execute(select(Alert.id).where(Alert.source_ip == attacker_ip))
        ).scalars().all()
        assert len(alert_ids) >= 2, f"expected >=2 alerts, got {len(alert_ids)}"

        incident_ids = (
            await db.execute(
                select(IncidentAlert.incident_id)
                .where(IncidentAlert.alert_id.in_(alert_ids))
                .distinct()
            )
        ).scalars().all()
        assert len(incident_ids) == 1, f"expected 1 incident, got {len(incident_ids)}"

        incident = await db.get(Incident, incident_ids[0])
        techniques = (
            await db.execute(
                select(Alert.mitre_technique_id)
                .join(IncidentAlert, IncidentAlert.alert_id == Alert.id)
                .where(IncidentAlert.incident_id == incident.id)
            )
        ).scalars().all()
        techniques = {t for t in techniques if t}

        assert "T1046" in techniques, f"missing port-scan technique: {techniques}"
        assert "T1110" in techniques, f"missing brute-force technique: {techniques}"
        assert incident.risk_score > 0, "incident risk score not computed"

        return {
            "incident_id": incident.id,
            "title": incident.title,
            "risk_score": incident.risk_score,
            "alerts": len(alert_ids),
            "techniques": sorted(techniques),
        }


async def test_multi_stage_attack_correlates_to_single_incident():
    await _setup()
    ip = _unique_ip()
    await _run_attack_chain(ip)
    result = await _assert_single_incident(ip)
    assert result["risk_score"] > 0


async def _main() -> None:
    await _setup()
    ip = _unique_ip()
    print(f"Simulating attack chain from {ip} (port scan -> brute force)...")
    await _run_attack_chain(ip)
    result = await _assert_single_incident(ip)
    print("[PASS] multi-stage attack correlated into a single incident:")
    for k, v in result.items():
        print(f"   {k}: {v}")


if __name__ == "__main__":
    import asyncio

    asyncio.run(_main())
