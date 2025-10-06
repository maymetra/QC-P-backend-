# app/crud/crud_knowledge_base.py
from sqlalchemy.orm import Session
from app.db import models
from app.schemas import knowledge_base as kb_schema

def get_all_items(db: Session):
    """
    Получить все элементы базы знаний.
    """
    return db.query(models.KnowledgeBaseItem).all()

def create_kb_item(db: Session, item: kb_schema.KnowledgeBaseItemCreate):
    """
    Создать новый элемент в базе знаний.
    """
    db_item = models.KnowledgeBaseItem(
        category=item.category,
        item=item.item
    )
    db.add(db_item)
    db.commit()
    db.refresh(db_item)
    return db_item

def get_kb_item_by_text(db: Session, item_text: str):
    """
    Найти элемент по его тексту.
    """
    return db.query(models.KnowledgeBaseItem).filter(models.KnowledgeBaseItem.item == item_text).first()