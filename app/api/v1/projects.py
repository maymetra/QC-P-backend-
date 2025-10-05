# app/api/v1/projects.py
from fastapi import APIRouter, Depends, HTTPException
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
    current_user: models.User = Depends(deps.get_current_user) # <-- ЗАЩИТА!
):
    """
    Получить список проектов, принадлежащих текущему пользователю.
    """
    projects = crud_project.get_projects_by_owner(
        db=db, owner_id=current_user.id, skip=skip, limit=limit
    )
    return projects

@router.post("/", response_model=project_schema.Project)
def create_project(
    project: project_schema.ProjectCreate,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(deps.get_current_user) # <-- ЗАЩИТА!
):
    """
    Создать новый проект для текущего пользователя.
    """
    return crud_project.create_project(db=db, project=project, owner_id=current_user.id)