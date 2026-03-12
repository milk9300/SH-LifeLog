from pydantic import BaseModel
from typing import Optional
from datetime import datetime

class BrainstormBase(BaseModel):
    content: str
    tags: Optional[str] = None
    status: str = "inbox"

class BrainstormCreate(BrainstormBase):
    pass

class BrainstormUpdate(BaseModel):
    content: Optional[str] = None
    tags: Optional[str] = None
    status: Optional[str] = None

class Brainstorm(BrainstormBase):
    id: int
    created_at: datetime

    class Config:
        from_attributes = True
