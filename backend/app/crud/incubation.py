from sqlalchemy.orm import Session
from .. import models, schemas
from typing import List, Optional

def get_incubation(db: Session, incubation_id: int):
    return db.query(models.Incubation).filter(models.Incubation.id == incubation_id).first()

def get_incubations(db: Session, skip: int = 0, limit: int = 100, result: Optional[str] = None):
    query = db.query(models.Incubation)
    if result:
        query = query.filter(models.Incubation.result == result)
    return query.order_by(models.Incubation.created_at.desc()).offset(skip).limit(limit).all()

def create_incubation(db: Session, incubation: schemas.IncubationCreate):
    db_incubation = models.Incubation(**incubation.model_dump())
    db.add(db_incubation)
    db.commit()
    db.refresh(db_incubation)
    return db_incubation

def update_incubation(db: Session, incubation_id: int, incubation: schemas.IncubationUpdate):
    db_incubation = get_incubation(db, incubation_id=incubation_id)
    if not db_incubation:
        return None
    
    update_data = incubation.model_dump(exclude_unset=True)
    for key, value in update_data.items():
        setattr(db_incubation, key, value)
        
    db.commit()
    db.refresh(db_incubation)
    return db_incubation

def delete_incubation(db: Session, incubation_id: int):
    db_incubation = get_incubation(db, incubation_id=incubation_id)
    if db_incubation:
        db.delete(db_incubation)
        db.commit()
    return db_incubation
