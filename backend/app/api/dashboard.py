from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from ..core.database import get_db
from ..crud import dashboard as crud

router = APIRouter()

@router.get("/stats")
def read_dashboard_stats(db: Session = Depends(get_db)):
    return crud.get_dashboard_stats(db)
