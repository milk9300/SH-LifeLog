from sqlalchemy.orm import Session
from .. import models, schemas
from typing import List

def get_graveyard(db: Session, graveyard_id: int):
    return db.query(models.ProjectGraveyard).filter(models.ProjectGraveyard.id == graveyard_id).first()

def get_graveyards(db: Session, skip: int = 0, limit: int = 100, project_id: int = None):
    query = db.query(models.ProjectGraveyard)
    if project_id:
        query = query.filter(models.ProjectGraveyard.project_id == project_id)
    return query.order_by(models.ProjectGraveyard.created_at.desc()).offset(skip).limit(limit).all()

def create_graveyard(db: Session, graveyard: schemas.ProjectGraveyardCreate):
    db_graveyard = models.ProjectGraveyard(**graveyard.model_dump())
    db.add(db_graveyard)
    db.commit()
    db.refresh(db_graveyard)
    
    # Update project status as well
    project = db.query(models.Project).filter(models.Project.id == graveyard.project_id).first()
    if project:
        project.status = 'graveyard'
        db.commit()
        
    return db_graveyard

def update_graveyard(db: Session, graveyard_id: int, graveyard: schemas.ProjectGraveyardUpdate):
    db_graveyard = get_graveyard(db, graveyard_id=graveyard_id)
    if not db_graveyard:
        return None
    
    update_data = graveyard.model_dump(exclude_unset=True)
    for key, value in update_data.items():
        setattr(db_graveyard, key, value)
        
    db.commit()
    db.refresh(db_graveyard)
    return db_graveyard

def delete_graveyard(db: Session, graveyard_id: int):
    db_graveyard = get_graveyard(db, graveyard_id=graveyard_id)
    if db_graveyard:
        db.delete(db_graveyard)
        db.commit()
    return db_graveyard
