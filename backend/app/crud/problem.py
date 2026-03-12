from sqlalchemy.orm import Session
from .. import models, schemas

def get_problems(db: Session, skip: int = 0, limit: int = 100):
    return db.query(models.Problem).offset(skip).limit(limit).all()

def get_problem(db: Session, problem_id: int):
    return db.query(models.Problem).filter(models.Problem.id == problem_id).first()

def create_problem(db: Session, problem: schemas.ProblemCreate):
    db_problem = models.Problem(**problem.dict())
    db.add(db_problem)
    db.commit()
    db.refresh(db_problem)
    return db_problem

def update_problem(db: Session, problem_id: int, problem: schemas.ProblemUpdate):
    db_problem = db.query(models.Problem).filter(models.Problem.id == problem_id).first()
    if db_problem:
        update_data = problem.dict(exclude_unset=True)
        for key, value in update_data.items():
            setattr(db_problem, key, value)
        db.commit()
        db.refresh(db_problem)
    return db_problem

def delete_problem(db: Session, problem_id: int):
    db_problem = db.query(models.Problem).filter(models.Problem.id == problem_id).first()
    if db_problem:
        db.delete(db_problem)
        db.commit()
    return db_problem
