from pydantic import BaseModel
from typing import Optional
from datetime import datetime

class IncubationBase(BaseModel):
    title: str
    brainstorm_id: Optional[int] = None
    problem: Optional[str] = None
    competitor_gap: Optional[str] = None
    one_page_doc: Optional[str] = None
    mvp_status: Optional[str] = "planning"
    demo_url: Optional[str] = None
    repo_url: Optional[str] = None
    user_feedback: Optional[str] = None
    result: Optional[str] = "experiment"
    current_step: Optional[int] = 1
    insights_summary: Optional[str] = None
    startup_plan_content: Optional[str] = None

class IncubationCreate(IncubationBase):
    pass

class IncubationUpdate(BaseModel):
    title: Optional[str] = None
    problem: Optional[str] = None
    competitor_gap: Optional[str] = None
    one_page_doc: Optional[str] = None
    mvp_status: Optional[str] = None
    demo_url: Optional[str] = None
    repo_url: Optional[str] = None
    user_feedback: Optional[str] = None
    result: Optional[str] = None
    current_step: Optional[int] = None
    insights_summary: Optional[str] = None
    startup_plan_content: Optional[str] = None

class Incubation(IncubationBase):
    id: int
    created_at: datetime

    class Config:
        from_attributes = True
