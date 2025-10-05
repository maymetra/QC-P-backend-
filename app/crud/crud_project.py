# app/crud/crud_project.py
from sqlalchemy.orm import Session
from app.db import models
from app.schemas import project as project_schema

def get_projects_by_owner(db: Session, owner_id: int, skip: int = 0, limit: int = 100):
    """
    Получить список проектов для конкретного пользователя.
    """
    return db.query(models.Project).filter(models.Project.owner_id == owner_id).offset(skip).limit(limit).all()

def create_project(db: Session, project: project_schema.ProjectCreate, owner_id: int):
    """
    Создать новый проект для пользователя.
    """
    db_project = models.Project(
        **project.model_dump(),  # Распаковываем все поля из Pydantic схемы
        owner_id=owner_id
    )
    db.add(db_project)
    db.commit()
    db.refresh(db_project)
    return db_project