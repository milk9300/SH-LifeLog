from sqlalchemy.orm import Session
from .. import models, schemas

def _attach_progress(db: Session, project: models.Project):
    tasks = db.query(models.Task).filter(models.Task.project_id == project.id).all()
    if not tasks:
        project.progress = 0
    else:
        done_count = len([t for t in tasks if t.status == 'done'])
        project.progress = int((done_count / len(tasks)) * 100)
    return project

def get_projects(db: Session, skip: int = 0, limit: int = 100):
    projects = db.query(models.Project).order_by(models.Project.created_at.desc()).offset(skip).limit(limit).all()
    for p in projects:
        _attach_progress(db, p)
    return projects

def get_project(db: Session, project_id: int):
    project = db.query(models.Project).filter(models.Project.id == project_id).first()
    if project:
        _attach_progress(db, project)
    return project

def create_project(db: Session, project: schemas.ProjectCreate):
    db_project = models.Project(**project.dict())
    db.add(db_project)
    db.commit()
    db.refresh(db_project)
    db_project.progress = 0
    return db_project

def update_project(db: Session, project_id: int, project: schemas.ProjectUpdate):
    db_project = db.query(models.Project).filter(models.Project.id == project_id).first()
    if db_project:
        update_data = project.dict(exclude_unset=True)
        for key, value in update_data.items():
            setattr(db_project, key, value)
        db.commit()
        db.refresh(db_project)
        _attach_progress(db, db_project)
    return db_project

def delete_project(db: Session, project_id: int):
    db_project = db.query(models.Project).filter(models.Project.id == project_id).first()
    if db_project:
        # 删除该项目的关联任务
        db.query(models.Task).filter(models.Task.project_id == project_id).delete()
        db.delete(db_project)
        db.commit()
    return db_project
