from sqlalchemy import Column, Integer, String, Text, ForeignKey, DateTime
from .base import Base, get_now

class ProjectGraveyard(Base):
    __tablename__ = "project_graveyards"

    id = Column(Integer, primary_key=True, index=True)
    project_id = Column(Integer, ForeignKey("projects.id"), index=True)
    reason = Column(Text, nullable=True)
    lessons = Column(Text, nullable=True)
    created_at = Column(DateTime(timezone=True), default=get_now)
