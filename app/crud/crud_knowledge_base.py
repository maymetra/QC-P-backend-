# app/crud/crud_knowledge_base.py
from sqlalchemy.orm import Session
from app.db import models

def get_all_items(db: Session):
    """
    Получить все элементы базы знаний.
    """
    return db.query(models.KnowledgeBaseItem).all()