from pydantic import BaseModel
from typing import Optional
from datetime import datetime

class ArticleBase(BaseModel):
    title: Optional[str] = None
    content: Optional[str] = None
    category: Optional[str] = "technical"
    status: Optional[str] = "draft"
    tags: Optional[str] = None
    problem_id: Optional[int] = None
    project_id: Optional[int] = None
    plan_id: Optional[int] = None
    milestone_id: Optional[int] = None

class ArticleCreate(ArticleBase):
    pass

class ArticleUpdate(BaseModel):
    title: Optional[str] = None
    content: Optional[str] = None
    category: Optional[str] = None
    status: Optional[str] = None
    tags: Optional[str] = None
    problem_id: Optional[int] = None
    project_id: Optional[int] = None
    plan_id: Optional[int] = None
    milestone_id: Optional[int] = None

class Article(ArticleBase):
    id: int
    created_at: datetime
    updated_at: Optional[datetime] = None

    class Config:
        from_attributes = True
