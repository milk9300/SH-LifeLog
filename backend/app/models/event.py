from sqlalchemy import Column, Integer, String, DateTime
from .base import Base, get_now

class Event(Base):
    __tablename__ = 'events'

    id = Column(Integer, primary_key=True, index=True)
    title = Column(String, nullable=False)
    progress = Column(Integer, default=0)
    created_at = Column(DateTime, default=get_now)
