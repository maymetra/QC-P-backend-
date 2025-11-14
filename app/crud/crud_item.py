# app/crud/crud_item.py
from sqlalchemy.orm import Session
from app.db import models
from app.schemas import item as item_schema
from app.crud import crud_history  # <-- 1. Импортируем

def get_items_by_project(db: Session, project_id: int, skip: int = 0, limit: int = 100):
    """Получить все задачи для указанного проекта."""
    return db.query(models.Item).filter(models.Item.project_id == project_id).offset(skip).limit(limit).all()


# 2. Добавляем user_name в аргументы
def create_project_item(db: Session, item: item_schema.ItemCreate, project_id: int, user_name: str):
    """Создать новую задачу для проекта."""
    db_item = models.Item(**item.model_dump(), project_id=project_id)
    db.add(db_item)
    db.commit()
    db.refresh(db_item)

    # --- 3. ЛОГИРОВАНИЕ ЗДЕСЬ ---
    crud_history.create_event(
        db=db,
        project_id=project_id,
        user_name=user_name,
        event_type="item_added",
        details=f"Item added: '{db_item.item}'"
    )
    # ---

    return db_item


# 4. Добавляем user_name и project_id в аргументы
def update_item(db: Session, item_id: int, item_in: item_schema.ItemUpdate, user_name: str, project_id: int):
    """Обновить задачу."""
    db_item = db.query(models.Item).filter(models.Item.id == item_id).first()
    if db_item:
        old_status = db_item.status  # Запоминаем старый статус

        update_data = item_in.model_dump(exclude_unset=True)
        for field, value in update_data.items():
            setattr(db_item, field, value)
        db.add(db_item)
        db.commit()
        db.refresh(db_item)

        # --- 5. ЛОГИРОВАНИЕ ЗДЕСЬ ---
        if "status" in update_data and old_status != db_item.status:
            crud_history.create_event(
                db=db,
                project_id=project_id,
                user_name=user_name,
                event_type="item_status_updated",
                details=f"Item '{db_item.item}' status changed from '{old_status}' to '{db_item.status}'."
            )
        # ---

    return db_item


# 6. Добавляем user_name и project_id в аргументы
def delete_item(db: Session, item_id: int, user_name: str, project_id: int):
    """Удалить задачу."""
    db_item = db.query(models.Item).filter(models.Item.id == item_id).first()
    if db_item:
        item_name = db_item.item  # Запоминаем имя

        db.delete(db_item)
        db.commit()

        # --- 7. ЛОГИРОВАНИЕ ЗДЕСЬ ---
        crud_history.create_event(
            db=db,
            project_id=project_id,
            user_name=user_name,
            event_type="item_deleted",
            details=f"Item deleted: '{item_name}'"
        )
        # ---
    return db_item