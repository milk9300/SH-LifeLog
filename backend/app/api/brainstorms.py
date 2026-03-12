from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List, Optional
from ..core.database import get_db
from .. import schemas
from ..crud import brainstorm as crud

router = APIRouter()

@router.get("/stats")
def read_brainstorm_stats(db: Session = Depends(get_db)):
    return crud.get_brainstorm_stats(db)

@router.get("/", response_model=List[schemas.Brainstorm])
def read_brainstorms(skip: int = 0, limit: int = 100, status: Optional[str] = None, db: Session = Depends(get_db)):
    return crud.get_brainstorms(db, skip=skip, limit=limit, status=status)

@router.get("/{brainstorm_id}", response_model=schemas.Brainstorm)
def read_brainstorm(brainstorm_id: int, db: Session = Depends(get_db)):
    db_brainstorm = crud.get_brainstorm(db, brainstorm_id=brainstorm_id)
    if not db_brainstorm:
        raise HTTPException(status_code=404, detail="Brainstorm not found")
    return db_brainstorm

@router.post("/", response_model=schemas.Brainstorm)
def create_brainstorm(brainstorm: schemas.BrainstormCreate, db: Session = Depends(get_db)):
    return crud.create_brainstorm(db=db, brainstorm=brainstorm)

@router.put("/{brainstorm_id}", response_model=schemas.Brainstorm)
def update_brainstorm(brainstorm_id: int, brainstorm: schemas.BrainstormUpdate, db: Session = Depends(get_db)):
    db_brainstorm = crud.update_brainstorm(db=db, brainstorm_id=brainstorm_id, brainstorm=brainstorm)
    if not db_brainstorm:
        raise HTTPException(status_code=404, detail="Brainstorm not found")
    return db_brainstorm

@router.delete("/{brainstorm_id}")
def delete_brainstorm(brainstorm_id: int, db: Session = Depends(get_db)):
    crud.delete_brainstorm(db=db, brainstorm_id=brainstorm_id)
    return {"detail": "Brainstorm deleted"}
