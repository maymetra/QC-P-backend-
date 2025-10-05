# app/crud/crud_item.py
from sqlalchemy.orm import Session
from app.db import models
from app.schemas import item as item_schema

def get_items_by_project(db: Session, project_id: int, skip: int = 0, limit: int = 100):
    """Получить все задачи для указанного проекта."""
    return db.query(models.Item).filter(models.Item.project_id == project_id).offset(skip).limit(limit).all()

def create_project_item(db: Session, item: item_schema.ItemCreate, project_id: int):
    """Создать новую задачу для проекта."""
    db_item = models.Item(**item.model_dump(), project_id=project_id)
    db.add(db_item)
    db.commit()
    db.refresh(db_item)
    return db_item

def update_item(db: Session, item_id: int, item_in: item_schema.ItemUpdate):
    """Обновить задачу."""
    db_item = db.query(models.Item).filter(models.Item.id == item_id).first()
    if db_item:
        update_data = item_in.model_dump(exclude_unset=True)
        for field, value in update_data.items():
            setattr(db_item, field, value)
        db.add(db_item)
        db.commit()
        db.refresh(db_item)
    return db_item

def delete_item(db: Session, item_id: int):
    """Удалить задачу."""
    db_item = db.query(models.Item).filter(models.Item.id == item_id).first()
    if db_item:
        db.delete(db_item)
        db.commit()
    return db_item