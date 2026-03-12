from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List, Optional
from ..core.database import get_db
from .. import schemas
from ..crud import plan as crud

router = APIRouter()

# --- Plans ---
@router.get("/", response_model=List[schemas.LongTermPlan])
def read_plans(skip: int = 0, limit: int = 100, status: Optional[str] = None, db: Session = Depends(get_db)):
    return crud.get_plans(db, skip=skip, limit=limit, status=status)

@router.get("/{plan_id}", response_model=schemas.LongTermPlan)
def read_plan(plan_id: int, db: Session = Depends(get_db)):
    db_plan = crud.get_plan(db, plan_id=plan_id)
    if not db_plan:
        raise HTTPException(status_code=404, detail="Plan not found")
    return db_plan

@router.post("/", response_model=schemas.LongTermPlan)
def create_plan(plan: schemas.LongTermPlanCreate, db: Session = Depends(get_db)):
    return crud.create_plan(db=db, plan=plan)

@router.put("/{plan_id}", response_model=schemas.LongTermPlan)
def update_plan(plan_id: int, plan: schemas.LongTermPlanUpdate, db: Session = Depends(get_db)):
    db_plan = crud.update_plan(db=db, plan_id=plan_id, plan=plan)
    if not db_plan:
        raise HTTPException(status_code=404, detail="Plan not found")
    return db_plan

@router.delete("/{plan_id}")
def delete_plan(plan_id: int, db: Session = Depends(get_db)):
    crud.delete_plan(db=db, plan_id=plan_id)
    return {"detail": "Plan deleted"}

# --- Milestones ---
@router.get("/{plan_id}/milestones", response_model=List[schemas.PlanMilestone])
def read_milestones(plan_id: int, skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    return crud.get_milestones(db, plan_id=plan_id, skip=skip, limit=limit)
