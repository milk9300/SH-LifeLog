from pydantic import BaseModel
from typing import Optional
from datetime import datetime

class LongTermPlanBase(BaseModel):
    title: str
    description: Optional[str] = None
    start_date: Optional[str] = None
    target_date: Optional[str] = None
    status: str = "active"

class LongTermPlanCreate(LongTermPlanBase):
    pass

class LongTermPlanUpdate(BaseModel):
    title: Optional[str] = None
    description: Optional[str] = None
    start_date: Optional[str] = None
    target_date: Optional[str] = None
    status: Optional[str] = None

class LongTermPlan(LongTermPlanBase):
    id: int
    created_at: datetime
    updated_at: Optional[datetime] = None

    class Config:
        from_attributes = True

class PlanMilestoneBase(BaseModel):
    plan_id: int
    title: str
    status: str = "todo"
    order_index: int = 0

class PlanMilestoneCreate(PlanMilestoneBase):
    pass

class PlanMilestoneUpdate(BaseModel):
    title: Optional[str] = None
    status: Optional[str] = None
    order_index: Optional[int] = None

class PlanMilestone(PlanMilestoneBase):
    id: int
    created_at: datetime
    updated_at: Optional[datetime] = None

    class Config:
        from_attributes = True
