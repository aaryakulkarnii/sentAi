"""Tier 3 exit criterion: a CSV upload produces detections that correlate into an
incident, and an AI investigation produces a complete, persisted package
(timeline, MITRE map, IOCs, remediation, executive summary).

Runs in zero-infra mode (SQLite + in-memory Redis), LLM falls back to templates
when no GROQ_API_KEY is set. Direct run: `python -m tests.integration.test_investigation`.
"""

from sqlalchemy import func, select

from app.agents.graph import run_investigation
from app.core.config import settings
from app.db.postgres import AsyncSessionLocal, init_db
from app.db.redis import init_redis
from app.ingestion.csv_ingest import ingest_csv, sample_csv
from app.ingestion.pipeline import init_engines
from app.models.alert import Alert
from app.models.incident import Incident, IncidentAlert
from app.services.detection.behavioral import BehavioralEngine
from app.services.detection.sigma_engine import SigmaEngine


async def _setup() -> None:
    assert settings.DEV_MODE
    await init_db()
    await init_redis()
    init_engines(SigmaEngine(rules_dir=settings.SIGMA_RULES_DIR), BehavioralEngine())


async def _latest_incident_id() -> str:
    async with AsyncSessionLocal() as db:
        # Most recently created incident (the sample attacker IP).
        inc = (
            await db.execute(select(Incident).order_by(Incident.created_at.desc()).limit(1))
        ).scalar_one_or_none()
        assert inc is not None, "no incident created from sample CSV"
        n = (
            await db.execute(
                select(func.count())
                .select_from(IncidentAlert)
                .where(IncidentAlert.incident_id == inc.id)
            )
        ).scalar_one()
        assert n >= 2, f"expected correlated incident, got {n} alert(s)"
        return inc.id


async def test_csv_upload_then_investigation_produces_full_package():
    await _setup()
    result = await ingest_csv(sample_csv().encode())
    assert result["alerts"] >= 2, f"sample CSV should raise >=2 alerts, got {result}"

    incident_id = await _latest_incident_id()
    out = await run_investigation(incident_id)

    assert out["attack_timeline"], "timeline empty"
    assert out["mitre_mappings"], "no MITRE mappings"
    assert out["executive_summary"], "no executive summary"
    assert out["remediation"].get("immediate_actions"), "no remediation"

    # Persisted and retrievable.
    async with AsyncSessionLocal() as db:
        from app.models.investigation import Investigation

        inv = (
            await db.execute(
                select(Investigation)
                .where(Investigation.incident_id == incident_id)
                .order_by(Investigation.created_at.desc())
                .limit(1)
            )
        ).scalar_one_or_none()
        assert inv is not None and inv.status == "complete"


async def _main() -> None:
    await _setup()
    print("Ingesting sample CSV (port scan + brute force)...")
    result = await ingest_csv(sample_csv().encode())
    print(f"  rows={result['rows']} alerts={result['alerts']} columns={result['detected_columns']}")
    incident_id = await _latest_incident_id()
    print(f"Running AI investigation on incident {incident_id[:8]}...")
    out = await run_investigation(incident_id)
    print("[PASS] investigation package:")
    print(f"   timeline steps : {len(out['attack_timeline'])}")
    print(f"   MITRE mapped   : {list(out['mitre_mappings'].keys())}")
    print(f"   IOCs           : {[i['value'] for i in out.get('iocs', [])]}")
    print(f"   remediation    : {out['remediation'].get('playbooks')}")
    print(f"   exec summary   : {out['executive_summary'][:140]}...")


if __name__ == "__main__":
    import asyncio

    asyncio.run(_main())
