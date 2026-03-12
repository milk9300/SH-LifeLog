from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List, Optional
from ..core.database import get_db
from .. import schemas
from ..crud import credential as crud

router = APIRouter()

@router.get("/", response_model=List[schemas.Credential])
def read_credentials(skip: int = 0, limit: int = 100, project_id: Optional[int] = None, category: Optional[str] = None, db: Session = Depends(get_db)):
    return crud.get_credentials(db, skip=skip, limit=limit, project_id=project_id, category=category)

@router.get("/{credential_id}", response_model=schemas.Credential)
def read_credential(credential_id: int, db: Session = Depends(get_db)):
    db_credential = crud.get_credential(db, credential_id=credential_id)
    if not db_credential:
        raise HTTPException(status_code=404, detail="Credential not found")
    return db_credential

@router.post("/", response_model=schemas.Credential)
def create_credential(credential: schemas.CredentialCreate, db: Session = Depends(get_db)):
    return crud.create_credential(db=db, credential=credential)

@router.put("/{credential_id}", response_model=schemas.Credential)
def update_credential(credential_id: int, credential: schemas.CredentialUpdate, db: Session = Depends(get_db)):
    db_credential = crud.update_credential(db=db, credential_id=credential_id, credential=credential)
    if not db_credential:
        raise HTTPException(status_code=404, detail="Credential not found")
    return db_credential

@router.delete("/{credential_id}")
def delete_credential(credential_id: int, db: Session = Depends(get_db)):
    crud.delete_credential(db=db, credential_id=credential_id)
    return {"detail": "Credential deleted"}
