from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List, Optional
from ..core.database import get_db
from .. import schemas
from ..crud import incubation as crud_incubation

router = APIRouter()

@router.get("/", response_model=List[schemas.Incubation])
def read_incubations(skip: int = 0, limit: int = 100, result: Optional[str] = None, db: Session = Depends(get_db)):
    return crud_incubation.get_incubations(db, skip=skip, limit=limit, result=result)

@router.get("/{incubation_id}", response_model=schemas.Incubation)
def read_incubation(incubation_id: int, db: Session = Depends(get_db)):
    db_incubation = crud_incubation.get_incubation(db, incubation_id=incubation_id)
    if not db_incubation:
        raise HTTPException(status_code=404, detail="Incubation not found")
    return db_incubation

@router.post("/", response_model=schemas.Incubation)
def create_incubation(incubation: schemas.IncubationCreate, db: Session = Depends(get_db)):
    return crud_incubation.create_incubation(db=db, incubation=incubation)

@router.put("/{incubation_id}", response_model=schemas.Incubation)
def update_incubation(incubation_id: int, incubation: schemas.IncubationUpdate, db: Session = Depends(get_db)):
    db_incubation = crud_incubation.update_incubation(db=db, incubation_id=incubation_id, incubation=incubation)
    if not db_incubation:
        raise HTTPException(status_code=404, detail="Incubation not found")
    return db_incubation

@router.delete("/{incubation_id}")
def delete_incubation(incubation_id: int, db: Session = Depends(get_db)):
    db_incubation = crud_incubation.delete_incubation(db=db, incubation_id=incubation_id)
    if not db_incubation:
        raise HTTPException(status_code=404, detail="Incubation not found")
    return {"detail": "Incubation deleted"}
