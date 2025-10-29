# app/crud/crud_project.py
from sqlalchemy.orm import Session
from app.db import models
from app.schemas import project as project_schema, item as item_schema
from app.crud import crud_template, crud_item



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

    return []


def create_project(db: Session, project: project_schema.ProjectCreate, owner_id: int):
    """
    Создать новый проект для пользователя.
    Если указан шаблон, создать задачи из него.
    """
    project_data = project.model_dump(exclude={"template", "basePlannedDate"})
    db_project = models.Project(**project_data, owner_id=owner_id)
    db.add(db_project)
    db.commit()
    db.refresh(db_project)

    if project.template:
        template = crud_template.get_template_by_name(db, name=project.template)
        if template:
            for item_name in template.items:
                item_in = item_schema.ItemCreate(
                    item=item_name,
                    planned_date=project.basePlannedDate
                )
                crud_item.create_project_item(db=db, item=item_in, project_id=db_project.id)

    return db_project

def delete_project(db: Session, project_id: int):
    """
    Удалить проект по ID.
    """
    db_project = db.query(models.Project).filter(models.Project.id == project_id).first()
    if db_project:
        db.delete(db_project)
        db.commit()
    return db_project

def get_project(db: Session, project_id: int, user: models.User):
    """
    Получить проект по ID с проверкой прав доступа.
    """
    project = db.query(models.Project).filter(models.Project.id == project_id).first()
    if not project:
        return None
    if user.role in ("admin", "auditor"):
        return project
    if user.role == "manager" and project.manager == user.name:
        return project
    return None

def update_project(db: Session, project_id: int, project_in: project_schema.ProjectUpdate):
    """
    Обновить проект.
    """
    db_project = db.query(models.Project).filter(models.Project.id == project_id).first()
    if db_project:
        update_data = project_in.model_dump(exclude_unset=True)
        for key, value in update_data.items():
            setattr(db_project, key, value)
        db.add(db_project)
        db.commit()
        db.refresh(db_project)
    return db_project