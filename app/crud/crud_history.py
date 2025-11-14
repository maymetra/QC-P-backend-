# app/crud/crud_history.py
from sqlalchemy.orm import Session
from app.db import models
from app.schemas import history as history_schema

def create_event(
    db: Session,
    project_id: int,
    user_name: str,
    event_type: str,
    details: str
):
    """Создать новую запись в истории проекта."""
    db_event = models.ProjectHistoryEvent(
        project_id=project_id,
        user_name=user_name,
        event_type=event_type,
        details=details
    )
    db.add(db_event)
    db.commit() # <-- УБЕДИТЕСЬ, ЧТО COMMIT ЗДЕСЬ ЕСТЬ
    db.refresh(db_event)
    return db_event

def get_events_for_project(db: Session, project_id: int):
    """Получить все события для проекта, отсортированные по времени."""
    return db.query(models.ProjectHistoryEvent)\
             .filter(models.ProjectHistoryEvent.project_id == project_id)\
             .order_by(models.ProjectHistoryEvent.timestamp.desc())\
             .all()