from sqlalchemy import String, Text
from sqlalchemy.orm import Mapped, mapped_column

from app.db.postgres import Base
from app.db.types import json_type


class MitreTechnique(Base):
    __tablename__ = "mitre_techniques"

    id: Mapped[str] = mapped_column(String(20), primary_key=True)  # e.g. T1059.001
    tactic: Mapped[str] = mapped_column(String(100))
    tactic_id: Mapped[str | None] = mapped_column(String(20))  # e.g. TA0002
    technique: Mapped[str] = mapped_column(String(200))
    sub_technique: Mapped[str | None] = mapped_column(String(200))
    description: Mapped[str | None] = mapped_column(Text)
    mitigation: Mapped[dict] = mapped_column(json_type(), default=dict)
    url: Mapped[str | None] = mapped_column(String(500))
