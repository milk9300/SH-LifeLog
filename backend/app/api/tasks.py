from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List, Optional
from ..core.database import get_db
from .. import schemas
from ..crud import task as crud
from ..crud import problem as crud_problem

router = APIRouter()

@router.get("/", response_model=List[schemas.Task])
def read_tasks(skip: int = 0, limit: int = 100, project_id: Optional[int] = None, is_today: Optional[bool] = None, status: Optional[str] = None, db: Session = Depends(get_db)):
    return crud.get_tasks(db, skip=skip, limit=limit, project_id=project_id, is_today=is_today, status=status)

@router.get("/{task_id}", response_model=schemas.Task)
def read_task(task_id: int, db: Session = Depends(get_db)):
    db_task = crud.get_task(db, task_id=task_id)
    if not db_task:
        raise HTTPException(status_code=404, detail="Task not found")
    return db_task

@router.post("/", response_model=schemas.Task)
def create_task(task: schemas.TaskCreate, db: Session = Depends(get_db)):
    return crud.create_task(db=db, task=task)

@router.put("/{task_id}", response_model=schemas.Task)
def update_task(task_id: int, task: schemas.TaskUpdate, db: Session = Depends(get_db)):
    db_task = crud.update_task(db=db, task_id=task_id, task=task)
    if not db_task:
        raise HTTPException(status_code=404, detail="Task not found")
    return db_task

@router.delete("/{task_id}")
def delete_task(task_id: int, db: Session = Depends(get_db)):
    crud.delete_task(db=db, task_id=task_id)
    return {"detail": "Task deleted"}


# ---------- 任务转知识沉淀（问题记录） ----------
@router.post("/{task_id}/convert-to-problem", response_model=schemas.Problem)
def convert_task_to_problem(task_id: int, db: Session = Depends(get_db)):
    """将项目任务转化为知识沉淀中的问题记录，开启知识沉淀流程"""
    db_task = crud.get_task(db, task_id=task_id)
    if not db_task:
        raise HTTPException(status_code=404, detail="Task not found")

    # 利用任务标题和描述生成问题记录
    problem_data = schemas.ProblemCreate(
        title=db_task.title,
        description=db_task.description or "",
        task_id=db_task.id,
        project_id=db_task.project_id,
        level="research",
        status="open"
    )
    return crud_problem.create_problem(db=db, problem=problem_data)
