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
    status: str
    risk_score: int
    assigned_to: str | None
    created_at: datetime
    updated_at: datetime

    model_config = {"from_attributes": True}


class IncidentNoteCreate(BaseModel):
    content: str
