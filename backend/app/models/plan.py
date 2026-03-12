from sqlalchemy import Column, Integer, String, DateTime, ForeignKey
from .base import Base, get_now

class LongTermPlan(Base):
    __tablename__ = 'long_term_plans'

    id = Column(Integer, primary_key=True, index=True)
    title = Column(String, nullable=False)
    description = Column(String, nullable=True)
    start_date = Column(String, nullable=True) 
    target_date = Column(String, nullable=True)
    status = Column(String, default="active") 
    created_at = Column(DateTime, default=get_now)
    updated_at = Column(DateTime, default=get_now, onupdate=get_now)

class PlanMilestone(Base):
    __tablename__ = 'plan_milestones'

    id = Column(Integer, primary_key=True, index=True)
    plan_id = Column(Integer, ForeignKey('long_term_plans.id'), nullable=False)
    title = Column(String, nullable=False)
    status = Column(String, default="todo") 
    order_index = Column(Integer, default=0)
    created_at = Column(DateTime, default=get_now)
    updated_at = Column(DateTime, default=get_now, onupdate=get_now)
