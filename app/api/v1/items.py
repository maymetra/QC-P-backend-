# app/api/v1/items.py
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List

from app.db import models
from app.db.session import get_db
from app.schemas import item as item_schema
from app.crud import crud_item
from app.api import deps

# Мы создаем два роутера: один для операций, привязанных к проекту,
# другой - для операций над конкретной задачей.
router = APIRouter()

@router.get("/projects/{project_id}/items", response_model=List[item_schema.Item], tags=["Items"])
def read_project_items(
    project_id: int,
    db: Session = Depends(get_db),
    skip: int = 0,
    limit: int = 100,
    current_user: models.User = Depends(deps.get_current_user)
):
    """Получить список всех задач для конкретного проекта."""
    items = crud_item.get_items_by_project(db, project_id=project_id, skip=skip, limit=limit)
    return items

@router.post("/projects/{project_id}/items", response_model=item_schema.Item, tags=["Items"])
def create_item_for_project(
    project_id: int,
    item: item_schema.ItemCreate,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(deps.get_current_user)
):
    """Создать новую задачу для проекта."""
    return crud_item.create_project_item(db=db, item=item, project_id=project_id)


@router.put("/items/{item_id}", response_model=item_schema.Item, tags=["Items"])
def update_item_details(
    item_id: int,
    item_in: item_schema.ItemUpdate,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(deps.get_current_user)
):
    """Обновить задачу по ее ID."""
    item = crud_item.update_item(db=db, item_id=item_id, item_in=item_in)
    if not item:
        raise HTTPException(status_code=404, detail="Item not found")
    return item

@router.delete("/items/{item_id}", status_code=status.HTTP_200_OK, tags=["Items"])
def delete_item(
    item_id: int,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(deps.get_current_user)
):
    """Удалить задачу по ее ID."""
    item = crud_item.delete_item(db=db, item_id=item_id)
    if not item:
        raise HTTPException(status_code=404, detail="Item not found")
    return {"detail": "Item deleted successfully"}