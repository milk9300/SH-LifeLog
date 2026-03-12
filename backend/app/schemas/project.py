from pydantic import BaseModel
from typing import Optional
from datetime import datetime

class ProjectBase(BaseModel):
    name: str
    description: Optional[str] = None
    reference_url: Optional[str] = None
    git_url: Optional[str] = None
    tech_stack: Optional[str] = None
    project_type: Optional[str] = None
    status: str = "active"

class ProjectCreate(ProjectBase):
    pass

class ProjectUpdate(BaseModel):
    name: Optional[str] = None
    description: Optional[str] = None
    reference_url: Optional[str] = None
    git_url: Optional[str] = None
    tech_stack: Optional[str] = None
    project_type: Optional[str] = None
    status: Optional[str] = None

class Project(ProjectBase):
    id: int
    created_at: datetime
    progress: Optional[int] = 0

    class Config:
        from_attributes = True
