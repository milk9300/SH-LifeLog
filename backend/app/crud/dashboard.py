from sqlalchemy.orm import Session
from .. import models

def get_dashboard_stats(db: Session):
    active_projects = db.query(models.Project).filter(models.Project.status == "active").count()
    today_remaining_tasks = db.query(models.Task).filter(models.Task.is_today == True, models.Task.status != "done").count()
    pending_brainstorms = db.query(models.Brainstorm).filter(models.Brainstorm.status == "inbox").count()
    
    active_plans = db.query(models.LongTermPlan).filter(models.LongTermPlan.status == "active").count()
    total_reflections = db.query(models.Article).count()
    total_credentials = db.query(models.Credential).count()
    
    return {
        "active_projects": active_projects,
        "today_remaining_tasks": today_remaining_tasks,
        "pending_brainstorms": pending_brainstorms,
        "active_plans": active_plans,
        "total_reflections": total_reflections,
        "total_credentials": total_credentials
    }
