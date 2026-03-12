from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List, Optional
from ..core.database import get_db
from .. import schemas
from ..crud import plan as crud

router = APIRouter()

@router.get("/{milestone_id}", response_model=schemas.PlanMilestone)
def read_milestone(milestone_id: int, db: Session = Depends(get_db)):
    db_milestone = crud.get_milestone(db, milestone_id=milestone_id)
    if not db_milestone:
        raise HTTPException(status_code=404, detail="Milestone not found")
    return db_milestone

@router.post("/", response_model=schemas.PlanMilestone)
def create_milestone(milestone: schemas.PlanMilestoneCreate, db: Session = Depends(get_db)):
    return crud.create_milestone(db=db, milestone=milestone)

@router.put("/{milestone_id}", response_model=schemas.PlanMilestone)
def update_milestone(milestone_id: int, milestone: schemas.PlanMilestoneUpdate, db: Session = Depends(get_db)):
    db_milestone = crud.update_milestone(db=db, milestone_id=milestone_id, milestone=milestone)
    if not db_milestone:
        raise HTTPException(status_code=404, detail="Milestone not found")
    return db_milestone

@router.delete("/{milestone_id}")
def delete_milestone(milestone_id: int, db: Session = Depends(get_db)):
    crud.delete_milestone(db=db, milestone_id=milestone_id)
    return {"detail": "Milestone deleted"}
