from datetime import datetime
from pydantic import BaseModel, ConfigDict


class UserResponse(BaseModel):
    id: str
    email: str
    full_name: str | None = None
    role: str
    created_at: datetime
    last_login: datetime | None = None

    model_config = ConfigDict(from_attributes=True)

class UserRoleUpdate(BaseModel):
    role: str
