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
        password_reset_needed=False  # Явно указываем
    )
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    return db_user


def update_user(db: Session, db_user: models.User, user_in: user_schema.UserCreate):
    """Обновить пользователя (Админом)."""
    update_data = user_in.model_dump(exclude_unset=True)

    if "password" in update_data and update_data["password"]:
        hashed_password = get_password_hash(update_data["password"])
        update_data["hashed_password"] = hashed_password
        del update_data["password"]
        # Если админ меняет пароль, сбрасываем флаг требования сброса
        db_user.password_reset_needed = False

    for field, value in update_data.items():
        setattr(db_user, field, value)

    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    return db_user


def mark_password_reset(db: Session, db_user: models.User):
    """Пометить, что пользователю нужен сброс пароля."""
    db_user.password_reset_needed = True
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    return db_user


def update_own_profile(db: Session, db_user: models.User, profile_in: user_schema.UserUpdateProfile):
    """Обновление пользователем своего профиля."""
    if profile_in.name:
        db_user.name = profile_in.name

    if profile_in.password:
        db_user.hashed_password = get_password_hash(profile_in.password)
        # Если пользователь сам сменил пароль, сбрасываем флаг (если он был)
        db_user.password_reset_needed = False

    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    return db_user