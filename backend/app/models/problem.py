from sqlalchemy import Column, Integer, String, Text, DateTime, ForeignKey
from .base import Base, get_now

class Problem(Base):
    __tablename__ = 'problems'
    
    id = Column(Integer, primary_key=True, index=True)
    title = Column(String, nullable=False)
    task_id = Column(Integer, ForeignKey('tasks.id'), nullable=True)
    project_id = Column(Integer, ForeignKey('projects.id'), nullable=True)
    description = Column(Text, nullable=True)
    level = Column(String, default="record")
    category = Column(String, default="bug")  # bug, performance, architecture, feature
    tags = Column(String, nullable=True)  # 逗号分隔的标签
    status = Column(String, default="open")
    
    # 进度与状态追踪
    knowledge_step = Column(Integer, default=1)  # 1-4 步进度
    article_id = Column(Integer, ForeignKey('articles.id'), nullable=True)  # 关联已生成的文章
    
    created_at = Column(DateTime, default=get_now)
