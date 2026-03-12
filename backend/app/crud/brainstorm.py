from sqlalchemy.orm import Session
from .. import models, schemas

def get_brainstorm_stats(db: Session):
    inbox = db.query(models.Brainstorm).filter(models.Brainstorm.status == "inbox").count()
    archived = db.query(models.Brainstorm).filter(models.Brainstorm.status == "archived").count()
    converted = db.query(models.Brainstorm).filter(models.Brainstorm.status == "converted").count()
    
    return {
        "inbox": inbox,
        "archived": archived,
        "converted": converted
    }

def get_brainstorms(db: Session, skip: int = 0, limit: int = 100, status: str = None):
    query = db.query(models.Brainstorm)
    if status is not None:
        query = query.filter(models.Brainstorm.status == status)
    return query.order_by(models.Brainstorm.created_at.desc()).offset(skip).limit(limit).all()

def get_brainstorm(db: Session, brainstorm_id: int):
    return db.query(models.Brainstorm).filter(models.Brainstorm.id == brainstorm_id).first()

def create_brainstorm(db: Session, brainstorm: schemas.BrainstormCreate):
    db_brainstorm = models.Brainstorm(**brainstorm.dict())
    db.add(db_brainstorm)
    db.commit()
    db.refresh(db_brainstorm)
    return db_brainstorm

def update_brainstorm(db: Session, brainstorm_id: int, brainstorm: schemas.BrainstormUpdate):
    db_brainstorm = db.query(models.Brainstorm).filter(models.Brainstorm.id == brainstorm_id).first()
    if db_brainstorm:
        update_data = brainstorm.dict(exclude_unset=True)
        for key, value in update_data.items():
            setattr(db_brainstorm, key, value)
        db.commit()
        db.refresh(db_brainstorm)
    return db_brainstorm

def delete_brainstorm(db: Session, brainstorm_id: int):
    db_brainstorm = db.query(models.Brainstorm).filter(models.Brainstorm.id == brainstorm_id).first()
    if db_brainstorm:
        db.delete(db_brainstorm)
        db.commit()
    return db_brainstorm
