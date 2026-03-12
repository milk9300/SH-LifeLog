from sqlalchemy import Column, Integer, String, DateTime
from .base import Base, get_now

class Project(Base):
    __tablename__ = 'projects'
    
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, index=True)
    description = Column(String, nullable=True)
    reference_url = Column(String, nullable=True)
    git_url = Column(String, nullable=True)
    tech_stack = Column(String, nullable=True)
    project_type = Column(String, nullable=True)  # Web, Mobile, AI, etc.
    status = Column(String, default="active")
    source = Column(String, default="direct") # direct, incubation
    created_at = Column(DateTime, default=get_now)

