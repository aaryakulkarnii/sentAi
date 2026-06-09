from datetime import datetime
from pydantic import BaseModel


class AlertResponse(BaseModel):
    id: str
    severity: str
    confidence: float
    source_ip: str | None
    dest_ip: str | None
    description: str | None
    mitre_technique_id: str | None
    status: str
    created_at: datetime

    model_config = {"from_attributes": True}


class AlertUpdate(BaseModel):
    status: str | None = None
