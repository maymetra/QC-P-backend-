# app/schemas/user.py
from pydantic import BaseModel
from typing import Optional

class UserCreate(BaseModel):
    username: str
    password: str
    name: str
    role: str

# Новая схема для обновления своего профиля
class UserUpdateProfile(BaseModel):
    name: Optional[str] = None
    password: Optional[str] = None

class User(BaseModel):
    id: int
    username: str
    name: str
    role: str
    is_active: bool
    password_reset_needed: bool # <-- Добавлено поле

    class Config:
        from_attributes = True