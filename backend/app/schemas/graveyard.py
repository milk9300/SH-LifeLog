from pydantic import BaseModel
from typing import Optional
from datetime import datetime

class ProjectGraveyardBase(BaseModel):
    project_id: int
    reason: Optional[str] = None
    lessons: Optional[str] = None

class ProjectGraveyardCreate(ProjectGraveyardBase):
    pass

class ProjectGraveyardUpdate(BaseModel):
    reason: Optional[str] = None
    lessons: Optional[str] = None

class ProjectGraveyard(ProjectGraveyardBase):
    id: int
    created_at: datetime

    class Config:
        from_attributes = True
