from datetime import datetime
from pydantic import BaseModel, ConfigDict


class ApiKeyCreate(BaseModel):
    name: str

class ApiKeyResponse(BaseModel):
    id: str
    name: str
    prefix: str
    user_id: str
    is_active: bool
    created_at: datetime
    expires_at: datetime | None = None

    model_config = ConfigDict(from_attributes=True)

class ApiKeyCreateResponse(BaseModel):
    key: ApiKeyResponse
    secret_key: str  # Only returned once!
