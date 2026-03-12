from sqlalchemy import Column, Integer, String, Boolean, DateTime, Text
from .base import Base, get_now

class FocusRecord(Base):
    """
    时间管理专注记录模型
    完全脱离项目任务系统，独立记录日常琐事与专注事项
    """
    __tablename__ = 'focus_records'
    
    id = Column(Integer, primary_key=True, index=True)
    title = Column(String, nullable=False)           
    description = Column(Text, nullable=True)
    
    priority = Column(Integer, default=0)             # 0: Do First, 1: Schedule, 2: Delegate, 3: Don't Do
    status = Column(String, default="todo")          # todo, doing, done
    is_today = Column(Boolean, default=True)        # 是否显示在今日聚焦
    
    project_id = Column(Integer, nullable=True)      # 关联宏观项目
    plan_id = Column(Integer, nullable=True)         # 关联长期计划
    deadline = Column(DateTime, nullable=True)       # 截止日期
    
    created_at = Column(DateTime, default=get_now)
    updated_at = Column(DateTime, default=get_now, onupdate=get_now)
