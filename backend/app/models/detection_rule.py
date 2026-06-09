import uuid
from datetime import datetime, timezone

from sqlalchemy import Boolean, DateTime, ForeignKey, String, Text
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import Mapped, mapped_column

from app.db.postgres import Base


class DetectionRule(Base):
    __tablename__ = "detection_rules"

    id: Mapped[str] = mapped_column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    name: Mapped[str] = mapped_column(String(300), nullable=False)
    type: Mapped[str] = mapped_column(String(30))  # sigma/behavioral/anomaly
    definition: Mapped[dict] = mapped_column(JSONB, default=dict)
    severity: Mapped[str] = mapped_column(String(20), default="medium")
    mitre_technique_id: Mapped[str | None] = mapped_column(String, ForeignKey("mitre_techniques.id"), nullable=True)
    enabled: Mapped[bool] = mapped_column(Boolean, default=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc))
