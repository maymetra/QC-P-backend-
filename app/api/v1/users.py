# app/api/v1/users.py
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List

from app.db import models
from app.db.session import get_db
from app.schemas import user as user_schema
from app.crud import crud_user
from app.api import deps

router = APIRouter(prefix="/users", tags=["Users"])


@router.get("/", response_model=List[user_schema.User])
def read_users(
        db: Session = Depends(get_db),
        skip: int = 0,
        limit: int = 100,
        current_admin: models.User = Depends(deps.get_current_admin_user)
):
    """Получить список всех пользователей (только для админов)."""
    users = crud_user.get_users(db, skip=skip, limit=limit)
    return users

@router.get("/managers", response_model=List[user_schema.User])
def read_managers(
    db: Session = Depends(get_db),
    current_user: models.User = Depends(deps.get_current_auditor_or_admin_user)
):
    """Получить список всех менеджеров (для админов и аудиторов)."""
    managers = crud_user.get_managers(db)
    return managers


@router.put("/{user_id}", response_model=user_schema.User)
def update_user_data(
        user_id: int,
        user_in: user_schema.UserCreate,
        db: Session = Depends(get_db),
        current_admin: models.User = Depends(deps.get_current_admin_user)
):
    """Обновить пользователя (только для админов)."""
    db_user = crud_user.get_user(db, user_id=user_id)
    if not db_user:
        raise HTTPException(status_code=404, detail="User not found")

    user = crud_user.update_user(db=db, db_user=db_user, user_in=user_in)
    return user