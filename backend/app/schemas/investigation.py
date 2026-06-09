from datetime import datetime

from pydantic import BaseModel


class InvestigationTrigger(BaseModel):
    incident_id: str


class InvestigationResponse(BaseModel):
    id: str
    incident_id: str
    status: str
    risk_score: int
    agent_output: dict
    attack_timeline: dict
    mitre_mappings: dict
    iocs: dict
    remediation: dict
    created_at: datetime

    model_config = {"from_attributes": True}


class InvestigationStatus(BaseModel):
    incident_id: str
    status: str  # none | pending | running | complete | failed
    investigation_id: str | None = None
