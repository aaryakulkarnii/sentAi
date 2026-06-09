import uuid
from datetime import datetime, timezone

from sqlalchemy import DateTime, ForeignKey, Integer, String
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import Mapped, mapped_column

from app.db.postgres import Base


class Investigation(Base):
    __tablename__ = "investigations"

    id: Mapped[str] = mapped_column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    incident_id: Mapped[str] = mapped_column(String, ForeignKey("incidents.id"), nullable=False)
    agent_output: Mapped[dict] = mapped_column(JSONB, default=dict)
    attack_timeline: Mapped[dict] = mapped_column(JSONB, default=dict)
    mitre_mappings: Mapped[dict] = mapped_column(JSONB, default=dict)
    iocs: Mapped[dict] = mapped_column(JSONB, default=dict)
    remediation: Mapped[dict] = mapped_column(JSONB, default=dict)
    risk_score: Mapped[int] = mapped_column(Integer, default=0)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc))
