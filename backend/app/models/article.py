from sqlalchemy import Column, Integer, String, Text, DateTime, ForeignKey
from .base import Base, get_now

class Article(Base):
    __tablename__ = 'articles'
    
    id = Column(Integer, primary_key=True, index=True)
    title = Column(String, nullable=True)
    content = Column(Text, nullable=True)
    category = Column(String, default="technical")
    status = Column(String, default="draft")
    tags = Column(String, nullable=True)
    
    # 关联字段
    problem_id = Column(Integer, ForeignKey('problems.id'), nullable=True)
    project_id = Column(Integer, ForeignKey('projects.id'), nullable=True)
    plan_id = Column(Integer, ForeignKey('long_term_plans.id'), nullable=True)
    milestone_id = Column(Integer, ForeignKey('plan_milestones.id'), nullable=True)
    
    created_at = Column(DateTime, default=get_now)
    updated_at = Column(DateTime, default=get_now, onupdate=get_now)
