"""Correlation engine (Tier 2).

Groups alerts that share an entity (source IP / host) within a sliding time
window into a single incident, then (re)computes the incident's risk score from
its member alerts and the criticality of the assets involved.
"""

from __future__ import annotations

import uuid
from datetime import datetime, timedelta, timezone

import structlog
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.config import settings
from app.db.postgres import AsyncSessionLocal
from app.models.alert import Alert
from app.models.incident import Incident, IncidentAlert
from app.services.assets import get_criticality
from app.services.risk_scoring import compute_risk_score

logger = structlog.get_logger(__name__)

SEVERITY_ORDER = {"low": 0, "medium": 1, "high": 2, "critical": 3}
ACTIVE_STATUSES = ("open", "investigating")


async def handle_new_alert(alert_id: str) -> str | None:
    """Correlate a freshly-created alert. Returns the incident id if grouped."""
    async with AsyncSessionLocal() as db:
        alert = await db.get(Alert, alert_id)
        if alert is None:
            return None

        entity_ip = alert.source_ip
        if not entity_ip:
            # No correlatable entity — only escalate standalone criticals.
            if alert.severity == "critical":
                return await _create_incident(db, [alert], entity_ip)
            return None

        window_start = datetime.now(timezone.utc) - timedelta(seconds=settings.CORRELATION_WINDOW)

        # 1) Existing active incident already holding an alert from this entity?
        existing = await _find_incident_for_entity(db, entity_ip, window_start)
        if existing is not None:
            await _attach_alert(db, existing, alert)
            await recompute_incident_risk(db, existing)
            await db.commit()
            logger.info("alert_correlated", incident_id=existing, alert_id=alert.id, entity=entity_ip)
            return existing

        # 2) Enough sibling alerts from the same entity to form a cluster?
        siblings = await _unlinked_siblings(db, entity_ip, window_start)
        if len(siblings) >= settings.CORRELATION_MIN_ALERTS:
            incident_id = await _create_incident(db, siblings, entity_ip)
            logger.info(
                "incident_created", incident_id=incident_id, entity=entity_ip, alerts=len(siblings)
            )
            return incident_id

        # 3) Single critical alert still warrants its own incident.
        if alert.severity == "critical":
            return await _create_incident(db, [alert], entity_ip)

        return None


# ── helpers ──────────────────────────────────────────────────────────────────
async def _find_incident_for_entity(
    db: AsyncSession, entity_ip: str, window_start: datetime
) -> str | None:
    q = (
        select(IncidentAlert.incident_id)
        .join(Alert, Alert.id == IncidentAlert.alert_id)
        .join(Incident, Incident.id == IncidentAlert.incident_id)
        .where(Alert.source_ip == entity_ip)
        .where(Incident.status.in_(ACTIVE_STATUSES))
        .where(Incident.created_at >= window_start)
        .order_by(Incident.created_at.desc())
        .limit(1)
    )
    return (await db.execute(q)).scalar_one_or_none()


async def _unlinked_siblings(
    db: AsyncSession, entity_ip: str, window_start: datetime
) -> list[Alert]:
    linked_subq = select(IncidentAlert.alert_id)
    q = (
        select(Alert)
        .where(Alert.source_ip == entity_ip)
        .where(Alert.created_at >= window_start)
        .where(Alert.id.not_in(linked_subq))
        .order_by(Alert.created_at.asc())
    )
    return list((await db.execute(q)).scalars().all())


async def _attach_alert(db: AsyncSession, incident_id: str, alert: Alert) -> None:
    exists = await db.get(IncidentAlert, {"incident_id": incident_id, "alert_id": alert.id})
    if exists is None:
        db.add(IncidentAlert(incident_id=incident_id, alert_id=alert.id))


async def _create_incident(db: AsyncSession, alerts: list[Alert], entity_ip: str | None) -> str:
    incident_id = str(uuid.uuid4())
    dominant = max(alerts, key=lambda a: SEVERITY_ORDER.get(a.severity, 0))
    title = _build_title(alerts, entity_ip)

    incident = Incident(
        id=incident_id,
        title=title,
        description=f"Auto-correlated from {len(alerts)} alert(s) sharing entity {entity_ip or 'n/a'}.",
        status="open",
        risk_score=0,
        created_at=datetime.now(timezone.utc),
        updated_at=datetime.now(timezone.utc),
    )
    db.add(incident)
    await db.flush()

    for a in alerts:
        await _attach_alert(db, incident_id, a)

    await recompute_incident_risk(db, incident_id)
    await db.commit()
    return incident_id


def _build_title(alerts: list[Alert], entity_ip: str | None) -> str:
    techniques = {a.mitre_technique_id for a in alerts if a.mitre_technique_id}
    src = entity_ip or "unknown source"
    if len(alerts) == 1:
        return alerts[0].description or f"Security incident from {src}"
    if len(techniques) >= 2:
        return f"Multi-stage attack from {src} ({len(alerts)} alerts)"
    return f"Correlated activity from {src} ({len(alerts)} alerts)"


async def recompute_incident_risk(db: AsyncSession, incident_id: str) -> int:
    """Recompute an incident's risk as the max risk across its member alerts."""
    incident = await db.get(Incident, incident_id)
    if incident is None:
        return 0

    alert_ids = (
        await db.execute(
            select(IncidentAlert.alert_id).where(IncidentAlert.incident_id == incident_id)
        )
    ).scalars().all()

    best = 0
    for aid in alert_ids:
        alert = await db.get(Alert, aid)
        if alert is None:
            continue
        criticality = await get_criticality(db, host=None, ip=alert.source_ip)
        score = compute_risk_score(
            severity=alert.severity,
            confidence=alert.confidence,
            asset_criticality=criticality,
        )
        best = max(best, score)

    incident.risk_score = best
    incident.updated_at = datetime.now(timezone.utc)
    return best
