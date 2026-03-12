from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List, Optional
from ..core.database import get_db
from ..schemas.focus import FocusRecord, FocusRecordCreate, FocusRecordUpdate
from ..crud import focus as crud_focus

router = APIRouter()

@router.get("/", response_model=List[FocusRecord])
def read_focus_records(
    is_today: Optional[bool] = None,
    status: Optional[str] = None,
    limit: int = 100,
    db: Session = Depends(get_db)
):
    return crud_focus.get_focus_records(db, is_today=is_today, status=status, limit=limit)

@router.post("/", response_model=FocusRecord)
def create_focus_record(record: FocusRecordCreate, db: Session = Depends(get_db)):
    return crud_focus.create_focus_record(db, record)

@router.patch("/{record_id}", response_model=FocusRecord)
def update_focus_record(record_id: int, record: FocusRecordUpdate, db: Session = Depends(get_db)):
    db_record = crud_focus.update_focus_record(db, record_id, record)
    if db_record is None:
        raise HTTPException(status_code=404, detail="Focus record not found")
    return db_record

@router.delete("/{record_id}")
def delete_focus_record(record_id: int, db: Session = Depends(get_db)):
    success = crud_focus.delete_focus_record(db, record_id)
    if not success:
        raise HTTPException(status_code=404, detail="Focus record not found")
    return {"message": "Focus record deleted"}
