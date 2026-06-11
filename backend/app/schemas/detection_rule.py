from datetime import datetime
from pydantic import BaseModel, ConfigDict


class DetectionRuleCreate(BaseModel):
    name: str
    type: str
    definition: dict
    severity: str = "medium"
    mitre_technique_id: str | None = None
    enabled: bool = True

class DetectionRuleUpdate(BaseModel):
    enabled: bool

class DetectionRuleResponse(BaseModel):
    id: str
    name: str
    type: str
    definition: dict
    severity: str
    mitre_technique_id: str | None = None
    enabled: bool
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)
