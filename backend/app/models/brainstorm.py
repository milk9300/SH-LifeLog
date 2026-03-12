from sqlalchemy import Column, Integer, Text, String, DateTime
from .base import Base, get_now

class Brainstorm(Base):
    __tablename__ = 'brainstorms'
    
    id = Column(Integer, primary_key=True, index=True)
    content = Column(Text, nullable=False)           
    tags = Column(String, nullable=True)             
    status = Column(String, default="inbox")         
    created_at = Column(DateTime, default=get_now)
