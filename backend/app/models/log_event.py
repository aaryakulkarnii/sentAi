from sqlalchemy import String, Integer, DateTime
from sqlalchemy.orm import Mapped, mapped_column
from sqlalchemy.dialects.postgresql import JSONB
from app.db.postgres import Base
import uuid
from datetime import datetime

class LogEvent(Base):
    __tablename__ = "log_events"

    id: Mapped[str] = mapped_column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    timestamp: Mapped[datetime] = mapped_column(DateTime(timezone=True), index=True)
    source_type: Mapped[str | None] = mapped_column(String, index=True)
    event_type: Mapped[str | None] = mapped_column(String, index=True)
    severity: Mapped[str | None] = mapped_column(String, index=True)
    
    source_ip: Mapped[str | None] = mapped_column(String)
    dest_ip: Mapped[str | None] = mapped_column(String)
    
    # Store the entire raw/normalized event here so it's searchable via JSONB operators
    data: Mapped[dict] = mapped_column(JSONB)
