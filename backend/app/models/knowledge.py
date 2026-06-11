from sqlalchemy import String, Integer
from sqlalchemy.orm import Mapped, mapped_column
from pgvector.sqlalchemy import Vector
from app.db.postgres import Base

class ThreatKnowledge(Base):
    __tablename__ = "threat_knowledge"
    
    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    external_id: Mapped[str] = mapped_column(String, index=True)
    title: Mapped[str] = mapped_column(String)
    text: Mapped[str] = mapped_column(String)
    source: Mapped[str] = mapped_column(String)
    embedding = mapped_column(Vector(768))
