# app/crud/crud_user.py
from sqlalchemy.orm import Session
from app.db import models
from app.schemas import user as user_schema
from app.core.security import get_password_hash


def get_user_by_username(db: Session, username: str):
    return db.query(models.User).filter(models.User.username == username).first()


def get_user(db: Session, user_id: int):
    return db.query(models.User).filter(models.User.id == user_id).first()


def get_users(db: Session, skip: int = 0, limit: int = 100):
    """Получить список всех пользователей."""
    return db.query(models.User).offset(skip).limit(limit).all()

def get_managers(db: Session):
    """Получить список всех пользователей с ролью 'manager'."""
    return db.query(models.User).filter(models.User.role == 'manager').all()


def create_user(db: Session, user: user_schema.UserCreate):
    hashed_password = get_password_hash(user.password)
    db_user = models.User(
        username=user.username,
        name=user.name,
        role=user.role,
        hashed_password=hashed_password,
    )
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    return db_user


def update_user(db: Session, db_user: models.User, user_in: user_schema.UserCreate):
    """Обновить данные пользователя."""
    update_data = user_in.model_dump(exclude_unset=True)

    if "password" in update_data and update_data["password"]:
        hashed_password = get_password_hash(update_data["password"])
        update_data["hashed_password"] = hashed_password
        del update_data["password"]

    for field, value in update_data.items():
        setattr(db_user, field, value)

    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    return db_user