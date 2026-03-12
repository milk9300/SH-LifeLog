from sqlalchemy.orm import Session
from .. import models, schemas

def get_credentials(db: Session, skip: int = 0, limit: int = 100, project_id: int = None, category: str = None):
    query = db.query(models.Credential)
    if project_id is not None:
        if project_id == -1:
            query = query.filter(models.Credential.project_id.is_(None))
        else:
            query = query.filter(models.Credential.project_id == project_id)
    if category is not None:
        query = query.filter(models.Credential.category == category)
    return query.order_by(models.Credential.created_at.desc()).offset(skip).limit(limit).all()

def get_credential(db: Session, credential_id: int):
    return db.query(models.Credential).filter(models.Credential.id == credential_id).first()

def create_credential(db: Session, credential: schemas.CredentialCreate):
    db_credential = models.Credential(**credential.dict())
    db.add(db_credential)
    db.commit()
    db.refresh(db_credential)
    return db_credential

def update_credential(db: Session, credential_id: int, credential: schemas.CredentialUpdate):
    db_credential = db.query(models.Credential).filter(models.Credential.id == credential_id).first()
    if db_credential:
        update_data = credential.dict(exclude_unset=True)
        for key, value in update_data.items():
            setattr(db_credential, key, value)
        db.commit()
        db.refresh(db_credential)
    return db_credential

def delete_credential(db: Session, credential_id: int):
    db_credential = db.query(models.Credential).filter(models.Credential.id == credential_id).first()
    if db_credential:
        db.delete(db_credential)
        db.commit()
    return db_credential
