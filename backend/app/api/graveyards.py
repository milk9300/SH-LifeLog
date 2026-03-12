from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List, Optional
from ..core.database import get_db
from .. import schemas
from ..crud import graveyard as crud_graveyard

router = APIRouter()

@router.get("/", response_model=List[schemas.ProjectGraveyard])
def read_graveyards(skip: int = 0, limit: int = 100, project_id: Optional[int] = None, db: Session = Depends(get_db)):
    return crud_graveyard.get_graveyards(db, skip=skip, limit=limit, project_id=project_id)

@router.get("/{graveyard_id}", response_model=schemas.ProjectGraveyard)
def read_graveyard(graveyard_id: int, db: Session = Depends(get_db)):
    db_graveyard = crud_graveyard.get_graveyard(db, graveyard_id=graveyard_id)
    if not db_graveyard:
        raise HTTPException(status_code=404, detail="Graveyard record not found")
    return db_graveyard

@router.post("/", response_model=schemas.ProjectGraveyard)
def create_graveyard(graveyard: schemas.ProjectGraveyardCreate, db: Session = Depends(get_db)):
    return crud_graveyard.create_graveyard(db=db, graveyard=graveyard)

@router.put("/{graveyard_id}", response_model=schemas.ProjectGraveyard)
def update_graveyard(graveyard_id: int, graveyard: schemas.ProjectGraveyardUpdate, db: Session = Depends(get_db)):
    db_graveyard = crud_graveyard.update_graveyard(db=db, graveyard_id=graveyard_id, graveyard=graveyard)
    if not db_graveyard:
        raise HTTPException(status_code=404, detail="Graveyard record not found")
    return db_graveyard

@router.delete("/{graveyard_id}")
def delete_graveyard(graveyard_id: int, db: Session = Depends(get_db)):
    db_graveyard = crud_graveyard.delete_graveyard(db=db, graveyard_id=graveyard_id)
    if not db_graveyard:
        raise HTTPException(status_code=404, detail="Graveyard record not found")
    return {"detail": "Graveyard record deleted"}
