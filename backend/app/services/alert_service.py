"""Alert creation – Postgres persistence, OpenSearch indexing, pub/sub."""

from __future__ import annotations

import uuid
from dataclasses import dataclass
from datetime import datetime, timezone

import structlog
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.config import settings
from app.db.postgres import AsyncSessionLocal
from app.db.redis import get_redis
from app.ingestion.schema import NormalizedEvent
from app.models.alert import Alert
from app.models.detection_rule import DetectionRule
from app.schemas.alert import AlertResponse
from app.services.detection.behavioral import BehavioralResult
from app.services.detection.sigma_engine import DetectionResult
from app.services.indexing import index_alert_document
from app.services.pubsub import publish_alert

logger = structlog.get_logger(__name__)

Detection = DetectionResult | BehavioralResult


@dataclass
class AlertService:
    async def create_from_detection(
        self,
        event: NormalizedEvent,
        detection: Detection,
        raw_event_id: str | None,
    ) -> Alert | None:
        dedup_key = f"alert:dedup:{detection.rule_id}:{event.source_ip or event.host}"
        redis = get_redis()
        if await redis.set(dedup_key, "1", nx=True, ex=settings.ALERT_DEDUP_WINDOW):
            pass  # key was set – proceed
        else:
            logger.debug("alert_deduplicated", rule=detection.rule_id)
            return None

        async with AsyncSessionLocal() as db:
            rule_db_id = await self._ensure_rule(db, detection)

            mitre_id = await self._resolve_mitre_id(db, detection.mitre_technique_id)

            alert = Alert(
                id=str(uuid.uuid4()),
                rule_id=rule_db_id,
                severity=detection.severity,
                confidence=detection.confidence,
                source_ip=event.source_ip,
                dest_ip=event.dest_ip,
                raw_event_id=raw_event_id,
                mitre_technique_id=mitre_id,
                description=f"{detection.rule_name} on {event.host or event.source_ip or 'unknown host'}",
                status="open",
                created_at=datetime.now(timezone.utc),
            )
            db.add(alert)
            await db.commit()
            await db.refresh(alert)

            response = AlertResponse.model_validate(alert)
            alert_dict = response.model_dump(mode="json")
            alert_dict["id"] = alert.id

            await index_alert_document(
                {
                    "alert_id": alert.id,
                    "severity": alert.severity,
                    "confidence": alert.confidence,
                    "source_ip": alert.source_ip,
                    "dest_ip": alert.dest_ip,
                    "description": alert.description,
                    "rule_id": detection.rule_id,
                    "mitre_technique_id": alert.mitre_technique_id,
                    "status": alert.status,
                }
            )
            await publish_alert(alert_dict)
            logger.info("alert_created", alert_id=alert.id, rule=detection.rule_id, severity=alert.severity)
            return alert

    async def _resolve_mitre_id(self, db: AsyncSession, technique_id: str | None) -> str | None:
        if not technique_id:
            return None
        from app.models.mitre import MitreTechnique

        row = await db.get(MitreTechnique, technique_id)
        return technique_id if row else None

    async def _ensure_rule(self, db: AsyncSession, detection: Detection) -> str | None:
        from sqlalchemy import select

        result = await db.execute(
            select(DetectionRule).where(DetectionRule.name == detection.rule_name)
        )
        existing = result.scalar_one_or_none()
        if existing:
            return existing.id

        mitre_id = await self._resolve_mitre_id(db, detection.mitre_technique_id)
        rule = DetectionRule(
            id=str(uuid.uuid4()),
            name=detection.rule_name,
            type=getattr(detection, "rule_type", "sigma"),
            definition={"rule_id": detection.rule_id},
            severity=detection.severity,
            mitre_technique_id=mitre_id,
            enabled=True,
        )
        db.add(rule)
        await db.flush()
        return rule.id


alert_service = AlertService()
