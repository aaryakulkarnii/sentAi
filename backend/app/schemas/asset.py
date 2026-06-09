from datetime import datetime

from pydantic import BaseModel, Field


class AssetCreate(BaseModel):
    hostname: str
    ip: str | None = None
    os: str | None = None
    criticality: int = Field(default=3, ge=1, le=5)
    owner: str | None = None


class AssetUpdate(BaseModel):
    hostname: str | None = None
    ip: str | None = None
    os: str | None = None
    criticality: int | None = Field(default=None, ge=1, le=5)
    owner: str | None = None


class AssetResponse(BaseModel):
    id: str
    hostname: str
    ip: str | None
    os: str | None
    criticality: int
    owner: str | None
    created_at: datetime

    model_config = {"from_attributes": True}
