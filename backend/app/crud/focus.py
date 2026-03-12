from sqlalchemy.orm import Session
from ..models.focus import FocusRecord
from ..schemas.focus import FocusRecordCreate, FocusRecordUpdate

def get_focus_records(db: Session, is_today: bool = None, status: str = None, limit: int = 100):
    query = db.query(FocusRecord)
    if is_today is not None:
        query = query.filter(FocusRecord.is_today == is_today)
    if status is not None:
        query = query.filter(FocusRecord.status == status)
    return query.order_by(FocusRecord.created_at.desc()).limit(limit).all()

def create_focus_record(db: Session, record: FocusRecordCreate):
    db_record = FocusRecord(**record.dict())
    db.add(db_record)
    db.commit()
    db.refresh(db_record)
    return db_record

def update_focus_record(db: Session, record_id: int, record: FocusRecordUpdate):
    db_record = db.query(FocusRecord).filter(FocusRecord.id == record_id).first()
    if not db_record:
        return None
    
    update_data = record.dict(exclude_unset=True)
    for key, value in update_data.items():
        setattr(db_record, key, value)
    
    db.commit()
    db.refresh(db_record)
    return db_record

def delete_focus_record(db: Session, record_id: int):
    db_record = db.query(FocusRecord).filter(FocusRecord.id == record_id).first()
    if db_record:
        db.delete(db_record)
        db.commit()
        return True
    return False
