from sqlalchemy import Column, Integer, String, Boolean, DateTime, ForeignKey, Text
from .base import Base, get_now

class Task(Base):
    __tablename__ = 'tasks'
    
    id = Column(Integer, primary_key=True, index=True)
    title = Column(String, nullable=False)           
    description = Column(Text, nullable=True)
    project_id = Column(Integer, ForeignKey('projects.id'), nullable=True) 
    
    is_today = Column(Boolean, default=False)        
    due_date = Column(DateTime, nullable=True)
    priority = Column(Integer, default=0)
    
    status = Column(String, default="todo")          
    task_type = Column(String, default="feature")    
    category = Column(String, default="task")         # project / long_term / daily / task / memo
    deliverable = Column(String, nullable=True)
    
    created_at = Column(DateTime, default=get_now)
    updated_at = Column(DateTime, default=get_now, onupdate=get_now)
