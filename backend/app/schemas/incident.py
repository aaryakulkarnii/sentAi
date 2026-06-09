from datetime import datetime

from pydantic import BaseModel


class IncidentCreate(BaseModel):
    title: str
    description: str | None = None
    alert_ids: list[str] = []


class IncidentUpdate(BaseModel):
    title: str | None = None
    status: str | None = None
    assigned_to: str | None = None


class IncidentResponse(BaseModel):
    id: str
    title: str
    description: str | None = None
    status: str
    risk_score: int
    assigned_to: str | None
    created_at: datetime
    updated_at: datetime

    model_config = {"from_attributes": True}


class IncidentDetailResponse(IncidentResponse):
    alert_count: int = 0
    technique_ids: list[str] = []


class IncidentNoteCreate(BaseModel):
    content: str


class IncidentNoteResponse(BaseModel):
    id: str
    incident_id: str
    author_id: str
    content: str
    created_at: datetime

    model_config = {"from_attributes": True}


class StatusUpdate(BaseModel):
    status: str


class AssignUpdate(BaseModel):
    assigned_to: str | None = None


class TimelineEvent(BaseModel):
    timestamp: datetime
    technique_id: str | None = None
    description: str | None = None
    source_ip: str | None = None
    severity: str
