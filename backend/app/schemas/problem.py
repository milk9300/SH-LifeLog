from pydantic import BaseModel
from typing import Optional, List
from datetime import datetime

class ProblemBase(BaseModel):
    title: str
    task_id: Optional[int] = None
    project_id: Optional[int] = None
    description: Optional[str] = None
    level: Optional[str] = "record"
    category: Optional[str] = "bug"
    tags: Optional[str] = None
    status: Optional[str] = "open"
    knowledge_step: Optional[int] = 1
    article_id: Optional[int] = None

class ProblemCreate(ProblemBase):
    pass

class ProblemUpdate(BaseModel):
    title: Optional[str] = None
    task_id: Optional[int] = None
    project_id: Optional[int] = None
    description: Optional[str] = None
    level: Optional[str] = None
    category: Optional[str] = None
    tags: Optional[str] = None
    status: Optional[str] = None
    knowledge_step: Optional[int] = None
    article_id: Optional[int] = None

class Problem(ProblemBase):
    id: int
    created_at: datetime

    class Config:
        from_attributes = True

class AIAssistRequest(BaseModel):
    step: int
    context: dict
    user_input: Optional[str] = None

class AIAssistResponse(BaseModel):
    reply: str
    suggestions: Optional[List[str]] = None

class ArticleGenerateRequest(BaseModel):
    content: Optional[str] = None
