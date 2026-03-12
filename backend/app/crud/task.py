from sqlalchemy.orm import Session
from .. import models, schemas

def get_tasks(db: Session, skip: int = 0, limit: int = 100, project_id: int = None, is_today: bool = None, status: str = None):
    query = db.query(models.Task)
    if project_id is not None:
        query = query.filter(models.Task.project_id == project_id)
    if is_today is not None:
        query = query.filter(models.Task.is_today == is_today)
    if status is not None:
        query = query.filter(models.Task.status == status)
    
    tasks = query.order_by(models.Task.updated_at.desc()).offset(skip).limit(limit).all()
    
    # 批量获取关联的 problem_id
    if tasks:
        task_ids = [t.id for t in tasks]
        problems = db.query(models.Problem).filter(models.Problem.task_id.in_(task_ids)).all()
        problem_map = {p.task_id: p.id for p in problems}
        for task in tasks:
            task.problem_id = problem_map.get(task.id)
            
    return tasks

def get_task(db: Session, task_id: int):
    task = db.query(models.Task).filter(models.Task.id == task_id).first()
    if task:
        problem = db.query(models.Problem).filter(models.Problem.task_id == task_id).first()
        task.problem_id = problem.id if problem else None
    return task

def create_task(db: Session, task: schemas.TaskCreate):
    db_task = models.Task(**task.dict())
    db.add(db_task)
    db.commit()
    db.refresh(db_task)
    return db_task

def update_task(db: Session, task_id: int, task: schemas.TaskUpdate):
    db_task = db.query(models.Task).filter(models.Task.id == task_id).first()
    if db_task:
        update_data = task.dict(exclude_unset=True)
        for key, value in update_data.items():
            setattr(db_task, key, value)
        db.commit()
        db.refresh(db_task)
    return db_task

def delete_task(db: Session, task_id: int):
    db_task = db.query(models.Task).filter(models.Task.id == task_id).first()
    if db_task:
        db.delete(db_task)
        db.commit()
    return db_task
