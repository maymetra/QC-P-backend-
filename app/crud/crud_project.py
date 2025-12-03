# app/crud/crud_project.py
import json
from sqlalchemy.orm import Session
from app.db import models
from app.schemas import project as project_schema, item as item_schema
from app.crud import crud_template, crud_item, crud_history
from datetime import date
from sqlalchemy import func


def get_projects(db: Session, user: models.User, skip: int = 0, limit: int = 100):
    """
    Получить список проектов с вычисленной датой завершения.
    """
    # 1. Создаем запрос с агрегацией: выбираем Проект и MAX(planned_date) из задач
    query = db.query(
        models.Project,
        func.max(models.Item.planned_date).label("max_date")
    ).outerjoin(models.Item).group_by(models.Project.id)

    # 2. Применяем фильтры по роли
    if user.role == "manager":
        query = query.filter(models.Project.manager == user.name)

    # 3. Получаем результаты
    results = query.offset(skip).limit(limit).all()

    # 4. Преобразуем результаты в список объектов Project с заполненным полем
    projects = []
    for p, max_date in results:
        p.planned_end_date = max_date  # Присваиваем вычисленное значение
        projects.append(p)

    return projects


def create_project(db: Session, project: project_schema.ProjectCreate, owner_id: int, user_name: str):
    """
    Создать новый проект для пользователя (без коммита).
    """
    project_data = project.model_dump(exclude={"template", "basePlannedDate"})
    db_project = models.Project(**project_data, owner_id=owner_id)
    db.add(db_project)

    # Выполняем flush, чтобы получить db_project.id до коммита
    db.flush()

    # Логирование создания проекта
    crud_history.create_event(
        db=db,
        project_id=db_project.id,
        user_name=user_name,
        event_type="project_created",
        details=f"Project '{db_project.name}' created."
    )

    if project.template:
        template = crud_template.get_template_by_name(db, name=project.template)
        if template:
            for item_name in template.items:
                item_in = item_schema.ItemCreate(
                    item=item_name,
                    planned_date=project.basePlannedDate
                )
                # Передаем user_name дальше
                crud_item.create_project_item(
                    db=db, item=item_in, project_id=db_project.id, user_name=user_name
                )

    return db_project  # commit и refresh будут в API


def delete_project(db: Session, project_id: int):
    """
    Удалить проект по ID.
    (Примечание: логирование удаления здесь не реализовано, но может быть добавлено)
    """
    db_project = db.query(models.Project).filter(models.Project.id == project_id).first()
    if db_project:
        db.delete(db_project)
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


def update_project(db: Session, project_id: int, project_in: project_schema.ProjectUpdate, user_name: str):
    """
    Обновить проект (без коммита).
    """
    db_project = db.query(models.Project).filter(models.Project.id == project_id).first()
    if db_project:
        # Логика сравнения ДО обновления
        old_status = db_project.status
        old_manager = db_project.manager

        update_data = project_in.model_dump(exclude_unset=True)

        if "status" in update_data:
            new_status = update_data["status"]
            # Если переводим в finished — ставим дату сегодня
            if new_status == "finished" and old_status != "finished":
                db_project.archived_at = date.today()
            # Если возвращаем из finished в работу — убираем дату
            elif new_status != "finished" and old_status == "finished":
                db_project.archived_at = None

        for key, value in update_data.items():
            setattr(db_project, key, value)

        db.add(db_project)  # Добавляем в сессию

        # --- ИЗМЕНЕНИЕ ЗДЕСЬ ---
        if "status" in update_data and old_status != db_project.status:
            # Сохраняем как JSON-строку
            details_json = json.dumps({
                "from": old_status,
                "to": db_project.status
            })
            crud_history.create_event(
                db=db,
                project_id=db_project.id,
                user_name=user_name,
                event_type="project_status_updated",
                details=details_json  # <-- Передаем JSON
            )

        if "manager" in update_data and old_manager != db_project.manager:
            # Оставляем как простую строку
            crud_history.create_event(
                db=db,
                project_id=db_project.id,
                user_name=user_name,
                event_type="project_manager_updated",
                details=f"Manager changed from '{old_manager or 'None'}' to '{db_project.manager or 'None'}'."
            )
        # --- КОНЕЦ ИЗМЕНЕНИЯ ---

    return db_project