# app/crud/crud_user.py
from sqlalchemy.orm import Session
from app.db import models
from app.schemas import user as user_schema
from app.core.security import get_password_hash

def get_user_by_username(db: Session, username: str):
    """
    Функция для получения пользователя по его имени.
    """
    return db.query(models.User).filter(models.User.username == username).first()

def create_user(db: Session, user: user_schema.UserCreate):
    """
    Функция для создания нового пользователя в базе данных.
    """
    # Хешируем пароль перед сохранением
    hashed_password = get_password_hash(user.password)
    # Создаем объект модели SQLAlchemy
    db_user = models.User(
        username=user.username,
        name=user.name,
        role=user.role,
        hashed_password=hashed_password,
    )
    # Добавляем в сессию и сохраняем в БД
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    return db_user