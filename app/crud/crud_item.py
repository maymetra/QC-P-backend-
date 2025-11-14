# app/crud/crud_item.py
from sqlalchemy.orm import Session
from app.db import models
from app.schemas import item as item_schema
from app.crud import crud_history


def get_items_by_project(db: Session, project_id: int, skip: int = 0, limit: int = 100):
    """Получить все задачи для указанного проекта."""
    return db.query(models.Item).filter(models.Item.project_id == project_id).offset(skip).limit(limit).all()


def create_project_item(db: Session, item: item_schema.ItemCreate, project_id: int, user_name: str):
    """Создать новую задачу для проекта (без коммита)."""
    db_item = models.Item(**item.model_dump(), project_id=project_id)
    db.add(db_item)

    # Логирование
    crud_history.create_event(
        db=db,
        project_id=project_id,
        user_name=user_name,
        event_type="item_added",
        details=f"Item added: '{item.item}'"
    )

    return db_item


def update_item(db: Session, item_id: int, item_in: item_schema.ItemUpdate, user_name: str, project_id: int):
    """Обновить задачу (без коммита)."""
    db_item = db.query(models.Item).filter(models.Item.id == item_id).first()
    if not db_item:
        return None

    # --- ИСПРАВЛЕННАЯ ЛОГИКА ---
    # exclude_unset=True гарантирует, что мы получаем dict ТОЛЬКО
    # с теми полями, которые прислал клиент (а не None по умолчанию)
    update_data = item_in.model_dump(exclude_unset=True)

    old_status = db_item.status  # Запоминаем для лога

    # Применяем обновления
    for field, value in update_data.items():
        setattr(db_item, field, value)

    db.add(db_item)  # Добавляем в сессию

    # Логирование, если статус изменился
    if "status" in update_data and old_status != db_item.status:
        crud_history.create_event(
            db=db,
            project_id=project_id,
            user_name=user_name,
            event_type="item_status_updated",
            details=f"Item '{db_item.item}' status changed from '{old_status}' to '{db_item.status}'."
        )

    return db_item


def delete_item(db: Session, item_id: int, user_name: str, project_id: int):
    """Удалить задачу (без коммита)."""
    db_item = db.query(models.Item).filter(models.Item.id == item_id).first()
    if db_item:
        item_name = db_item.item  # Запоминаем имя

        db.delete(db_item)  # Помечаем на удаление

        # Логирование
        crud_history.create_event(
            db=db,
            project_id=project_id,
            user_name=user_name,
            event_type="item_deleted",
            details=f"Item deleted: '{item_name}'"
        )
    return db_item