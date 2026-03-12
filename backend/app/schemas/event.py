from pydantic import BaseModel
from typing import Optional
from datetime import datetime

class EventBase(BaseModel):
    title: str
    progress: int = 0

class EventCreate(EventBase):
    pass

class EventUpdate(BaseModel):
    title: Optional[str] = None
    progress: Optional[int] = None

class Event(EventBase):
    id: int
    created_at: datetime

    class Config:
        from_attributes = True
