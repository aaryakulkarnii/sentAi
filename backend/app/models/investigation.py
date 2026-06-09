import uuid
from datetime import datetime, timezone

from sqlalchemy import DateTime, ForeignKey, Integer, String
from sqlalchemy.orm import Mapped, mapped_column

from app.db.postgres import Base
from app.db.types import json_type


class Investigation(Base):
    __tablename__ = "investigations"

    id: Mapped[str] = mapped_column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    incident_id: Mapped[str] = mapped_column(String, ForeignKey("incidents.id"), nullable=False)
    status: Mapped[str] = mapped_column(String(20), default="pending")
    agent_output: Mapped[dict] = mapped_column(json_type(), default=dict)
    attack_timeline: Mapped[dict] = mapped_column(json_type(), default=dict)
    mitre_mappings: Mapped[dict] = mapped_column(json_type(), default=dict)
    iocs: Mapped[dict] = mapped_column(json_type(), default=dict)
    remediation: Mapped[dict] = mapped_column(json_type(), default=dict)
    risk_score: Mapped[int] = mapped_column(Integer, default=0)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc))
