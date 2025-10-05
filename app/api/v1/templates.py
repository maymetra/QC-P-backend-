# app/api/v1/templates.py
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List

from app.db import models
from app.db.session import get_db
from app.schemas import template as template_schema
from app.crud import crud_template
from app.api import deps

router = APIRouter(prefix="/templates", tags=["Templates"])

@router.get("/", response_model=List[template_schema.Template])
def read_templates(
    db: Session = Depends(get_db),
    skip: int = 0,
    limit: int = 100,
    current_user: models.User = Depends(deps.get_current_user) # Доступно всем авторизованным
):
    """
    Получить список всех шаблонов.
    """
    templates = crud_template.get_templates(db, skip=skip, limit=limit)
    return templates

@router.post("/", response_model=template_schema.Template)
def create_template(
    template: template_schema.TemplateCreate,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(deps.get_current_auditor_or_admin_user) # Только для админов и аудиторов
):
    """
    Создать новый шаблон.
    """
    db_template = crud_template.get_template_by_name(db, name=template.name)
    if db_template:
        raise HTTPException(status_code=400, detail="Template with this name already exists")
    return crud_template.create_template(db=db, template=template, owner_id=current_user.id)


@router.put("/{template_id}", response_model=template_schema.Template)
def update_template(
    template_id: int,
    template_in: template_schema.TemplateCreate, # Используем схему создания для обновления
    db: Session = Depends(get_db),
    current_user: models.User = Depends(deps.get_current_auditor_or_admin_user)
):
    """
    Обновить шаблон по ID.
    """
    db_template = crud_template.update_template(db, template_id=template_id, template_in=template_in)
    if not db_template:
        raise HTTPException(status_code=404, detail="Template not found")
    return db_template


@router.delete("/{template_id}", status_code=status.HTTP_200_OK)
def delete_template(
    template_id: int,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(deps.get_current_auditor_or_admin_user) # Только для админов и аудиторов
):
    """
    Удалить шаблон по ID.
    """
    template_to_delete = crud_template.delete_template(db=db, template_id=template_id)
    if not template_to_delete:
        raise HTTPException(status_code=404, detail="Template not found")
    return {"detail": "Template deleted successfully"}