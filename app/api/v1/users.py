# app/api/v1/users.py
from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel
from sqlalchemy.orm import Session
from typing import List

from app.db import models
from app.db.session import get_db
from app.schemas import user as user_schema
from app.crud import crud_user
from app.api import deps

router = APIRouter(prefix="/users", tags=["Users"])

@router.get("/managers", response_model=List[user_schema.User])
def read_managers(
    db: Session = Depends(get_db),
    current_user: models.User = Depends(deps.get_current_auditor_or_admin_user)
):
    """Получить список всех менеджеров (для админов и аудиторов)."""
    managers = crud_user.get_managers(db)
    return managers

# app/api/v1/users.py

@router.put("/me", response_model=user_schema.User)
def update_current_user_profile(
    profile_in: user_schema.UserUpdateProfile,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(deps.get_current_user)
):
    """
    Обновить свой профиль (имя, пароль).
    """
    return crud_user.update_own_profile(db, db_user=current_user, profile_in=profile_in)

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

class NotificationCounts(BaseModel):
    unknown_managers: int
    password_resets: int


@router.get("/notifications/counts", response_model=NotificationCounts)
def get_notification_counts(
        db: Session = Depends(get_db),
        current_admin: models.User = Depends(deps.get_current_admin_user)
):
    """
    Получить количество уведомлений для админа.
    """
    # 1. Считаем запросы на сброс пароля
    reset_count = db.query(models.User).filter(models.User.password_reset_needed == True).count()

    # 2. Считаем неизвестных менеджеров
    all_users_names = {name for (name,) in db.query(models.User.name).all()}
    project_managers = {manager for (manager,) in
                        db.query(models.Project.manager).filter(models.Project.manager != None).distinct().all()}

    unknown_manager_count = len(project_managers - all_users_names)

    return NotificationCounts(
        unknown_managers=unknown_manager_count,
        password_resets=reset_count
    )