"""Behavioral detection using Redis-backed sliding-window counters."""

from __future__ import annotations

from dataclasses import dataclass

import structlog

from app.core.config import settings
from app.db.redis import get_redis
from app.ingestion.schema import NormalizedEvent

logger = structlog.get_logger(__name__)

FAILED_AUTH_TYPES = frozenset(
    {"USER_AUTH", "USER_LOGIN", "authentication_failure", "failed", "login_failed"}
)


@dataclass
class BehavioralResult:
    rule_id: str
    rule_name: str
    severity: str
    confidence: float
    mitre_technique_id: str | None
    rule_type: str = "behavioral"


class BehavioralEngine:
    """Stateful frequency-based detections backed by Redis."""

    async def evaluate(self, event: NormalizedEvent) -> list[BehavioralResult]:
        results: list[BehavioralResult] = []
        redis = get_redis()

        if event.source_ip:
            brute = await self._check_brute_force(redis, event)
            if brute:
                results.append(brute)

            spray = await self._check_password_spray(redis, event)
            if spray:
                results.append(spray)

            scan = await self._check_port_scan(redis, event)
            if scan:
                results.append(scan)

        return results

    async def _incr(self, redis, key: str, window: int) -> int:
        pipe = redis.pipeline()
        pipe.incr(key)
        pipe.expire(key, window)
        counts = await pipe.execute()
        return int(counts[0])

    async def _check_brute_force(self, redis, event: NormalizedEvent) -> BehavioralResult | None:
        if str(event.event_type).lower() not in FAILED_AUTH_TYPES:
            if event.raw.get("outcome") != "failure" and event.raw.get("result") != "failed":
                return None

        key = f"behav:brute:{event.source_ip}"
        count = await self._incr(redis, key, settings.BEHAVIORAL_BRUTE_FORCE_WINDOW)
        if count >= settings.BEHAVIORAL_BRUTE_FORCE_THRESHOLD:
            logger.info("brute_force_detected", ip=event.source_ip, count=count)
            return BehavioralResult(
                rule_id="behav-brute-force",
                rule_name="Brute Force Authentication",
                severity="high",
                confidence=min(1.0, count / settings.BEHAVIORAL_BRUTE_FORCE_THRESHOLD),
                mitre_technique_id="T1110",
            )
        return None

    async def _check_password_spray(self, redis, event: NormalizedEvent) -> BehavioralResult | None:
        if not event.user:
            return None
        if str(event.event_type).lower() not in FAILED_AUTH_TYPES:
            return None

        set_key = f"behav:spray:{event.source_ip}:users"
        await redis.sadd(set_key, event.user)
        await redis.expire(set_key, settings.BEHAVIORAL_PASSWORD_SPRAY_WINDOW)
        unique_users = await redis.scard(set_key)

        if unique_users >= settings.BEHAVIORAL_PASSWORD_SPRAY_THRESHOLD:
            logger.info("password_spray_detected", ip=event.source_ip, users=unique_users)
            return BehavioralResult(
                rule_id="behav-password-spray",
                rule_name="Password Spraying",
                severity="high",
                confidence=min(1.0, unique_users / settings.BEHAVIORAL_PASSWORD_SPRAY_THRESHOLD),
                mitre_technique_id="T1110.003",
            )
        return None

    async def _check_port_scan(self, redis, event: NormalizedEvent) -> BehavioralResult | None:
        if event.dest_port is None:
            return None

        set_key = f"behav:portscan:{event.source_ip}:ports"
        await redis.sadd(set_key, str(event.dest_port))
        await redis.expire(set_key, settings.BEHAVIORAL_PORT_SCAN_WINDOW)
        unique_ports = await redis.scard(set_key)

        if unique_ports >= settings.BEHAVIORAL_PORT_SCAN_THRESHOLD:
            logger.info("port_scan_detected", ip=event.source_ip, ports=unique_ports)
            return BehavioralResult(
                rule_id="behav-port-scan",
                rule_name="Port Scanning Activity",
                severity="medium",
                confidence=min(1.0, unique_ports / settings.BEHAVIORAL_PORT_SCAN_THRESHOLD),
                mitre_technique_id="T1046",
            )
        return None
