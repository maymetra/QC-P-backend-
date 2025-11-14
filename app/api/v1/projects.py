# app/api/v1/projects.py
from fastapi import APIRouter, Depends, status, HTTPException
from sqlalchemy.orm import Session
from typing import List

from app.db import models
from app.db.session import get_db
from app.schemas import project as project_schema
from app.crud import crud_project
from app.api import deps
from app.crud import crud_project, crud_history
from app.schemas import history as history_schema
from typing import List

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
    db_project = crud_project.create_project(db=db, project=project, owner_id=current_user.id)

    crud_history.create_event(
        db=db,
        project_id=db_project.id,
        user_name=current_user.name,
        event_type="project_created",
        details=f"Project '{db_project.name}' created."
    )

    return db_project

@router.get("/{project_id}", response_model=project_schema.Project)
def read_project(
        project_id: int,
        db: Session = Depends(get_db),
        current_user: models.User = Depends(deps.get_current_user)
):
    """
    Получить информацию о конкретном проекте по ID.
    """
    db_project = crud_project.get_project(db, project_id=project_id, user=current_user)
    if db_project is None:
        raise HTTPException(status_code=404, detail="Project not found or you don't have access")

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
    db_project = crud_project.get_project(db, project_id=project_id, user=current_user)
    if db_project is None:
        raise HTTPException(status_code=404, detail="Project not found or you don't have access")

    # --- ЛОГИРОВАНИЕ: Сохраняем старые значения ---
    old_status = db_project.status
    old_manager = db_project.manager
    # ---

    updated_project = crud_project.update_project(db=db, project_id=project_id, project_in=project_in)

    # --- ЛОГИРОВАНИЕ: Сравниваем и пишем в историю ---
    if old_status != updated_project.status:
        crud_history.create_event(
            db=db, project_id=updated_project.id, user_name=current_user.name,
            event_type="project_status_updated",
            details=f"Project status changed from '{old_status}' to '{updated_project.status}'."
        )

    if old_manager != updated_project.manager:
        crud_history.create_event(
            db=db, project_id=updated_project.id, user_name=current_user.name,
            event_type="project_manager_updated",
            details=f"Manager changed from '{old_manager or 'None'}' to '{updated_project.manager or 'None'}'."
        )
    # --- КОНЕЦ ЛОГИРОВАНИЯ ---

    return updated_project


# --- НОВЫЙ ЭНДПОИНТ ДЛЯ ИСТОРИИ ---
@router.get("/{project_id}/history", response_model=List[history_schema.ProjectHistoryEvent])
def read_project_history(
        project_id: int,
        db: Session = Depends(get_db),
        current_user: models.User = Depends(deps.get_current_user)
):
    """
    Получить историю изменений проекта.
    """
    # Проверяем, что у пользователя есть доступ к самому проекту
    db_project = crud_project.get_project(db, project_id=project_id, user=current_user)
    if db_project is None:
        raise HTTPException(status_code=404, detail="Project not found or you don't have access")

    return crud_history.get_events_for_project(db=db, project_id=project_id)