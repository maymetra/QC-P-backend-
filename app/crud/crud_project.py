# app/crud/crud_project.py
from sqlalchemy.orm import Session
from app.db import models
from app.schemas import project as project_schema, item as item_schema
from app.crud import crud_template, crud_item, crud_history



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


# 2. Добавляем user_name в аргументы
def create_project(db: Session, project: project_schema.ProjectCreate, owner_id: int, user_name: str):
    """
    Создать новый проект для пользователя.
    """
    project_data = project.model_dump(exclude={"template", "basePlannedDate"})
    db_project = models.Project(**project_data, owner_id=owner_id)
    db.add(db_project)
    db.commit()
    db.refresh(db_project)

    # --- 3. ЛОГИРОВАНИЕ СОЗДАНИЯ ПРОЕКТА ---
    crud_history.create_event(
        db=db,
        project_id=db_project.id,
        user_name=user_name,
        event_type="project_created",
        details=f"Project '{db_project.name}' created."
    )
    # ---

    if project.template:
        template = crud_template.get_template_by_name(db, name=project.template)
        if template:
            for item_name in template.items:
                item_in = item_schema.ItemCreate(
                    item=item_name,
                    planned_date=project.basePlannedDate
                )
                # 4. Передаем user_name дальше
                crud_item.create_project_item(
                    db=db, item=item_in, project_id=db_project.id, user_name=user_name
                )

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


# 5. Добавляем user_name в аргументы
def update_project(db: Session, project_id: int, project_in: project_schema.ProjectUpdate, user_name: str):
    """
    Обновить проект.
    """
    db_project = db.query(models.Project).filter(models.Project.id == project_id).first()
    if db_project:
        # --- 6. Логика сравнения ДО обновления ---
        old_status = db_project.status
        old_manager = db_project.manager

        update_data = project_in.model_dump(exclude_unset=True)
        for key, value in update_data.items():
            setattr(db_project, key, value)

        db.add(db_project)
        db.commit()
        db.refresh(db_project)

        # --- 7. Логика логирования ПОСЛЕ обновления ---
        if old_status != db_project.status:
            crud_history.create_event(
                db=db, project_id=db_project.id, user_name=user_name,
                event_type="project_status_updated",
                details=f"Project status changed from '{old_status}' to '{db_project.status}'."
            )

        if old_manager != db_project.manager:
            crud_history.create_event(
                db=db, project_id=db_project.id, user_name=user_name,
                event_type="project_manager_updated",
                details=f"Manager changed from '{old_manager or 'None'}' to '{db_project.manager or 'None'}'."
            )
        # ---

    return db_project