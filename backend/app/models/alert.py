import uuid
from datetime import datetime, timezone

from sqlalchemy import DateTime, Float, ForeignKey, Integer, String, Text
from sqlalchemy.orm import Mapped, mapped_column

from app.db.postgres import Base


class Alert(Base):
    __tablename__ = "alerts"

    id: Mapped[str] = mapped_column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    rule_id: Mapped[str | None] = mapped_column(String, ForeignKey("detection_rules.id"), nullable=True)
    severity: Mapped[str] = mapped_column(String(20))  # low/medium/high/critical
    confidence: Mapped[float] = mapped_column(Float, default=0.5)
    source_ip: Mapped[str | None] = mapped_column(String(45))
    dest_ip: Mapped[str | None] = mapped_column(String(45))
    host_id: Mapped[str | None] = mapped_column(String, ForeignKey("assets.id"), nullable=True)
    raw_event_id: Mapped[str | None] = mapped_column(String(255))  # Postgres LogEvent ID
    mitre_technique_id: Mapped[str | None] = mapped_column(String, ForeignKey("mitre_techniques.id"), nullable=True)
    status: Mapped[str] = mapped_column(String(20), default="open")
    description: Mapped[str | None] = mapped_column(Text)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc))
