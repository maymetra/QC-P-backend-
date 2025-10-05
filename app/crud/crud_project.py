# app/crud/crud_project.py
from sqlalchemy.orm import Session
from app.db import models
from app.schemas import project as project_schema


def get_projects(db: Session, user: models.User, skip: int = 0, limit: int = 100):
    """
    Получить список проектов на основе роли пользователя.
    - Админы/Аудиторы получают все проекты.
    - Менеджеры получают только проекты, где они указаны как 'manager'.
    """
    if user.role in ("admin", "auditor"):
        return db.query(models.Project).offset(skip).limit(limit).all()

    if user.role == "manager":
        return db.query(models.Project).filter(models.Project.manager == user.name).offset(skip).limit(limit).all()

    return []  # Другие роли (если появятся) не видят проектов


def create_project(db: Session, project: project_schema.ProjectCreate, owner_id: int):
    """
    Создать новый проект для пользователя.
    """
    db_project = models.Project(
        **project.model_dump(),
        owner_id=owner_id
    )
    db.add(db_project)
    db.commit()
    db.refresh(db_project)
    return db_project