# app/crud/crud_template.py
from sqlalchemy.orm import Session
from app.db import models
from app.schemas import template as template_schema

def get_template_by_name(db: Session, name: str):
    """
    Получить шаблон по имени.
    """
    return db.query(models.Template).filter(models.Template.name == name).first()

def get_templates(db: Session, skip: int = 0, limit: int = 100):
    """
    Получить список всех шаблонов.
    """
    return db.query(models.Template).offset(skip).limit(limit).all()

def create_template(db: Session, template: template_schema.TemplateCreate, owner_id: int):
    """
    Создать новый шаблон.
    """
    db_template = models.Template(
        **template.model_dump(),
        owner_id=owner_id
    )
    db.add(db_template)
    db.commit()
    db.refresh(db_template)
    return db_template

def delete_template(db: Session, template_id: int):
    """
    Удалить шаблон по ID.
    """
    db_template = db.query(models.Template).filter(models.Template.id == template_id).first()
    if db_template:
        db.delete(db_template)
        db.commit()
    return db_template

def update_template(db: Session, template_id: int, template_in: template_schema.TemplateCreate):
    """
    Обновить шаблон.
    """
    db_template = db.query(models.Template).filter(models.Template.id == template_id).first()
    if db_template:
        update_data = template_in.model_dump(exclude_unset=True)
        for key, value in update_data.items():
            setattr(db_template, key, value)
        db.add(db_template)
        db.commit()
        db.refresh(db_template)
    return db_template