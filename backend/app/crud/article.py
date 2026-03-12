from sqlalchemy.orm import Session
from .. import models, schemas

def get_articles(db: Session, skip: int = 0, limit: int = 100, category: str = None, project_id: int = None, plan_id: int = None, milestone_id: int = None):
    query = db.query(models.Article)
    if category:
        query = query.filter(models.Article.category == category)
    if project_id:
        query = query.filter(models.Article.project_id == project_id)
    if plan_id:
        query = query.filter(models.Article.plan_id == plan_id)
    if milestone_id:
        query = query.filter(models.Article.milestone_id == milestone_id)
    return query.order_by(models.Article.created_at.desc()).offset(skip).limit(limit).all()

def get_article(db: Session, article_id: int):
    return db.query(models.Article).filter(models.Article.id == article_id).first()

def create_article(db: Session, article: schemas.ArticleCreate):
    db_article = models.Article(**article.dict())
    db.add(db_article)
    db.commit()
    db.refresh(db_article)
    return db_article

def update_article(db: Session, article_id: int, article: schemas.ArticleUpdate):
    db_article = db.query(models.Article).filter(models.Article.id == article_id).first()
    if db_article:
        update_data = article.dict(exclude_unset=True)
        for key, value in update_data.items():
            setattr(db_article, key, value)
        db.commit()
        db.refresh(db_article)
    return db_article

def delete_article(db: Session, article_id: int):
    db_article = db.query(models.Article).filter(models.Article.id == article_id).first()
    if db_article:
        db.delete(db_article)
        db.commit()
    return db_article
