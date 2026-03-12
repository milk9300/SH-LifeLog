from pydantic import BaseModel
from typing import Optional
from datetime import datetime

class TaskBase(BaseModel):
    title: str
    description: Optional[str] = None
    project_id: Optional[int] = None
    is_today: bool = False
    due_date: Optional[datetime] = None
    priority: int = 0
    status: str = "todo"
    task_type: str = "feature"
    category: str = "task"
    deliverable: Optional[str] = None

class TaskCreate(TaskBase):
    pass

class TaskUpdate(BaseModel):
    title: Optional[str] = None
    description: Optional[str] = None
    project_id: Optional[int] = None
    is_today: Optional[bool] = None
    due_date: Optional[datetime] = None
    priority: Optional[int] = None
    status: Optional[str] = None
    task_type: Optional[str] = None
    category: Optional[str] = None
    deliverable: Optional[str] = None

class Task(TaskBase):
    id: int
    created_at: datetime
    updated_at: Optional[datetime] = None
    problem_id: Optional[int] = None

    class Config:
        from_attributes = True
