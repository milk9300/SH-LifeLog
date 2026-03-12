from sqlalchemy import Column, Integer, String, Text, DateTime, ForeignKey
from .base import Base, get_now

class Credential(Base):
    __tablename__ = 'credentials'

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, nullable=False)            
    category = Column(String, nullable=True)         
    username = Column(String, nullable=True)         
    project_id = Column(Integer, ForeignKey('projects.id'), nullable=True) 
    encrypted_data = Column(Text, nullable=False)    
    created_at = Column(DateTime, default=get_now)
    updated_at = Column(DateTime, default=get_now, onupdate=get_now)
