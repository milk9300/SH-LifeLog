from sqlalchemy.orm import Session
from .. import models, schemas

def get_plans(db: Session, skip: int = 0, limit: int = 100, status: str = None):
    query = db.query(models.LongTermPlan)
    if status is not None:
        query = query.filter(models.LongTermPlan.status == status)
    return query.order_by(models.LongTermPlan.created_at.desc()).offset(skip).limit(limit).all()

def get_plan(db: Session, plan_id: int):
    return db.query(models.LongTermPlan).filter(models.LongTermPlan.id == plan_id).first()

def create_plan(db: Session, plan: schemas.LongTermPlanCreate):
    db_plan = models.LongTermPlan(**plan.dict())
    db.add(db_plan)
    db.commit()
    db.refresh(db_plan)
    return db_plan

def update_plan(db: Session, plan_id: int, plan: schemas.LongTermPlanUpdate):
    db_plan = db.query(models.LongTermPlan).filter(models.LongTermPlan.id == plan_id).first()
    if db_plan:
        update_data = plan.dict(exclude_unset=True)
        for key, value in update_data.items():
            setattr(db_plan, key, value)
        db.commit()
        db.refresh(db_plan)
    return db_plan

def delete_plan(db: Session, plan_id: int):
    db_plan = db.query(models.LongTermPlan).filter(models.LongTermPlan.id == plan_id).first()
    if db_plan:
        db.query(models.PlanMilestone).filter(models.PlanMilestone.plan_id == plan_id).delete()
        db.delete(db_plan)
        db.commit()
    return db_plan

# --- Milestones ---
def get_milestones(db: Session, plan_id: int, skip: int = 0, limit: int = 100):
    query = db.query(models.PlanMilestone).filter(models.PlanMilestone.plan_id == plan_id)
    return query.order_by(models.PlanMilestone.order_index.asc()).offset(skip).limit(limit).all()

def get_milestone(db: Session, milestone_id: int):
    return db.query(models.PlanMilestone).filter(models.PlanMilestone.id == milestone_id).first()

def create_milestone(db: Session, milestone: schemas.PlanMilestoneCreate):
    db_milestone = models.PlanMilestone(**milestone.dict())
    db.add(db_milestone)
    db.commit()
    db.refresh(db_milestone)
    return db_milestone

def update_milestone(db: Session, milestone_id: int, milestone: schemas.PlanMilestoneUpdate):
    db_milestone = db.query(models.PlanMilestone).filter(models.PlanMilestone.id == milestone_id).first()
    if db_milestone:
        update_data = milestone.dict(exclude_unset=True)
        for key, value in update_data.items():
            setattr(db_milestone, key, value)
        db.commit()
        db.refresh(db_milestone)
    return db_milestone

def delete_milestone(db: Session, milestone_id: int):
    db_milestone = db.query(models.PlanMilestone).filter(models.PlanMilestone.id == milestone_id).first()
    if db_milestone:
        db.delete(db_milestone)
        db.commit()
    return db_milestone
