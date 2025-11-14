# app/api/v1/auth.py
from fastapi import APIRouter, Depends, HTTPException, status, Body
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.orm import Session

from app.db.session import get_db
from app.schemas import user as user_schema, token as token_schema
from app.crud import crud_user
from app.core import security

# Создаем роутер. Все эндпоинты в этом файле будут начинаться с /auth
router = APIRouter(prefix="/auth", tags=["Auth"])

@router.post("/register", response_model=user_schema.User)
def register_user(user: user_schema.UserCreate, db: Session = Depends(get_db)):
    """
    Эндпоинт для регистрации нового пользователя.
    """
    db_user = crud_user.get_user_by_username(db, username=user.username)
    if db_user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Username already registered",
        )
    return crud_user.create_user(db=db, user=user)


@router.post("/login", response_model=token_schema.Token)
def login_for_access_token(
    form_data: OAuth2PasswordRequestForm = Depends(), db: Session = Depends(get_db)
):
    """
    Эндпоинт для входа и получения JWT токена.
    FastAPI автоматически будет требовать username и password.
    """
    user = crud_user.get_user_by_username(db, username=form_data.username)
    if not user or not security.verify_password(form_data.password, user.hashed_password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )

    access_token = security.create_access_token(
        data={"sub": user.username, "name": user.name, "role": user.role}
    )
    return {"access_token": access_token, "token_type": "bearer"}

@router.post("/forgot-password")
def forgot_password(
        username: str = Body(..., embed=True),  # Ожидает JSON {"username": "..."}
        db: Session = Depends(get_db)
):
    """
    Запрос на сброс пароля. Устанавливает флаг для админа.
    """
    user = crud_user.get_user_by_username(db, username=username)
    if not user:
        # Из соображений безопасности можно вернуть 200, даже если юзера нет
        # но для внутреннего инструмента вернем ошибку для ясности
        raise HTTPException(status_code=404, detail="User not found")

    crud_user.mark_password_reset(db, user)
    return {"message": "Password reset requested. Please contact administrator."}