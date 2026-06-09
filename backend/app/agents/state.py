"""Shared investigation state passed between agent nodes."""

from typing import Any, TypedDict


class InvestigationState(TypedDict, total=False):
    incident_id: str
    incident: dict[str, Any]
    alerts: list[dict]
    entities: dict[str, list[str]]
    threat_intel: dict[str, Any]
    mitre_mappings: dict[str, Any]
    attack_timeline: list[dict]
    iocs: list[dict]
    remediation: dict[str, Any]
    executive_summary: str
    risk_score: int
    agent_log: list[dict]
