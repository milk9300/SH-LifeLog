from sqlalchemy import Column, Integer, String, Text, ForeignKey, DateTime
from .base import Base, get_now

class Incubation(Base):
    __tablename__ = "incubations"

    id = Column(Integer, primary_key=True, index=True)
    title = Column(String, index=True)
    brainstorm_id = Column(Integer, ForeignKey("brainstorms.id"), nullable=True)

    problem = Column(Text, nullable=True)
    competitor_gap = Column(Text, nullable=True)
    one_page_doc = Column(Text, nullable=True)

    # 孵化核心流程扩展
    current_step = Column(Integer, default=1)  # 1-5 步骤跟踪
    insights_summary = Column(Text, nullable=True) # 步骤 4 的关键洞察总结
    startup_plan_content = Column(Text, nullable=True) # 步骤 5 生成的计划书内容
    
    mvp_status = Column(String, default="planning") # planning, developing, testing, done
    demo_url = Column(String, nullable=True)
    repo_url = Column(String, nullable=True)

    user_feedback = Column(Text, nullable=True)

    result = Column(String, default="experiment") # discarded, experiment, project
    created_at = Column(DateTime(timezone=True), default=get_now)
