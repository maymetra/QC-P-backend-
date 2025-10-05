# app/api/v1/projects.py
from fastapi import APIRouter, Depends, status, HTTPException
from sqlalchemy.orm import Session
from typing import List

from app.db import models
from app.db.session import get_db
from app.schemas import project as project_schema
from app.crud import crud_project
from app.api import deps

router = APIRouter(prefix="/projects", tags=["Projects"])

@router.get("/", response_model=List[project_schema.Project])
def read_projects(
    db: Session = Depends(get_db),
    skip: int = 0,
    limit: int = 100,
    current_user: models.User = Depends(deps.get_current_user)
):
    """
    Получить список проектов в зависимости от роли текущего пользователя.
    """
    projects = crud_project.get_projects(db=db, user=current_user, skip=skip, limit=limit)
    return projects

@router.post("/", response_model=project_schema.Project)
def create_project_for_user(
    project: project_schema.ProjectCreate,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(deps.get_current_user)
):
    """
    Создать новый проект. Владельцем становится текущий пользователь.
    """
    return crud_project.create_project(db=db, project=project, owner_id=current_user.id)

@router.get("/{project_id}", response_model=project_schema.Project)
def read_project(
        project_id: int,
        db: Session = Depends(get_db),
        current_user: models.User = Depends(deps.get_current_user)
):
    """
    Получить информацию о конкретном проекте по ID.
    """
    db_project = crud_project.get_project(db, project_id=project_id)
    if db_project is None:
        raise HTTPException(status_code=404, detail="Project not found")

    # Тут можно добавить логику проверки прав доступа, если нужно,
    # но пока оставим так для простоты.

    return db_project

@router.delete("/{project_id}", status_code=status.HTTP_200_OK)
def delete_project(
    project_id: int,
    db: Session = Depends(get_db),
    current_admin: models.User = Depends(deps.get_current_admin_user) # <-- Только для админов!
):
    """
    Удалить проект по  ID.
    """
    project = crud_project.delete_project(db=db, project_id=project_id)
    if project is None:
        raise HTTPException(status_code=404, detail="Project not found")
    return {"detail": "Project deleted successfully"}

@router.put("/{project_id}", response_model=project_schema.Project)
def update_project(
        project_id: int,
        project_in: project_schema.ProjectUpdate,
        db: Session = Depends(get_db),
        current_user: models.User = Depends(deps.get_current_user)
):
    """
    Обновить проект по ID.
    """
    db_project = crud_project.get_project(db, project_id=project_id)
    if db_project is None:
        raise HTTPException(status_code=404, detail="Project not found")

    # В будущем здесь можно добавить проверку, что обновлять может только админ или менеджер проекта

    return crud_project.update_project(db=db, project_id=project_id, project_in=project_in)
