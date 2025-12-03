# app/api/v1/items.py
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List

from app.db import models
from app.db.session import get_db
from app.schemas import item as item_schema
from app.crud import crud_item, crud_project
from app.api import deps

router = APIRouter(tags=["Items"])


@router.get("/projects/{project_id}/items", response_model=List[item_schema.Item])
def read_project_items(
        project_id: int,
        db: Session = Depends(get_db),
        skip: int = 0,
        limit: int = 100,
        current_user: models.User = Depends(deps.get_current_user)
):
    """Получить список всех задач для конкретного проекта."""
    db_project = crud_project.get_project(db, project_id=project_id, user=current_user)
    if db_project is None:
        raise HTTPException(status_code=404, detail="Project not found or you don't have access")

    items = crud_item.get_items_by_project(db, project_id=project_id, skip=skip, limit=limit)
    return items


@router.post("/projects/{project_id}/items", response_model=item_schema.Item)
def create_item_for_project(
        project_id: int,
        item: item_schema.ItemCreate,
        db: Session = Depends(get_db),
        current_user: models.User = Depends(deps.get_current_user)
):
    """Создать новую задачу для проекта."""
    db_project = crud_project.get_project(db, project_id=project_id, user=current_user)
    if db_project is None:
        raise HTTPException(status_code=404, detail="Project not found or you don't have access")

    if db_project.status == 'finished':
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Cannot add items to an archived project"
        )

    db_item = crud_item.create_project_item(
        db=db, item=item, project_id=project_id, user_name=current_user.name
    )

    db.commit()
    db.refresh(db_item)

    return db_item


@router.put("/projects/{project_id}/items/{item_id}", response_model=item_schema.Item)
def update_item_details(
        item_id: int,
        project_id: int,
        item_in: item_schema.ItemUpdate,
        db: Session = Depends(get_db),
        current_user: models.User = Depends(deps.get_current_user)
):
    """Обновить задачу по ее ID."""
    db_project = crud_project.get_project(db, project_id=project_id, user=current_user)
    if db_project is None:
        raise HTTPException(status_code=404, detail="Project not found or you don't have access")

    item = crud_item.update_item(
        db=db, item_id=item_id, item_in=item_in, user_name=current_user.name, project_id=project_id
    )
    if not item:
        raise HTTPException(status_code=404, detail="Item not found")

    if item.project_id != project_id:
        raise HTTPException(status_code=403, detail="Item does not belong to this project")

    db.commit()
    db.refresh(item)

    return item


@router.delete("/projects/{project_id}/items/{item_id}", status_code=status.HTTP_200_OK)
def delete_item(
        item_id: int,
        project_id: int,
        db: Session = Depends(get_db),
        current_user: models.User = Depends(deps.get_current_user)
):
    """Удалить задачу по ее ID."""
    db_project = crud_project.get_project(db, project_id=project_id, user=current_user)
    if db_project is None:
        raise HTTPException(status_code=404, detail="Project not found or you don't have access")

    item_to_delete = db.query(models.Item).filter(models.Item.id == item_id).first()
    if not item_to_delete:
        raise HTTPException(status_code=404, detail="Item not found")
    if item_to_delete.project_id != project_id:
        raise HTTPException(status_code=403, detail="Item does not belong to this project")

    crud_item.delete_item(
        db=db, item_id=item_id, user_name=current_user.name, project_id=project_id
    )

    db.commit()

    return {"detail": "Item deleted successfully"}