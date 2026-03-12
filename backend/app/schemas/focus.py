from pydantic import BaseModel
from typing import Optional
from datetime import datetime

class FocusRecordBase(BaseModel):
    title: str
    description: Optional[str] = None
    priority: int = 0
    status: str = "todo"
    is_today: bool = True
    project_id: Optional[int] = None
    plan_id: Optional[int] = None
    deadline: Optional[datetime] = None

class FocusRecordCreate(FocusRecordBase):
    pass

class FocusRecordUpdate(BaseModel):
    title: Optional[str] = None
    description: Optional[str] = None
    priority: Optional[int] = None
    status: Optional[str] = None
    is_today: Optional[bool] = None
    project_id: Optional[int] = None
    plan_id: Optional[int] = None
    deadline: Optional[datetime] = None

class FocusRecord(FocusRecordBase):
    id: int
    created_at: datetime
    updated_at: Optional[datetime] = None

    class Config:
        from_attributes = True
