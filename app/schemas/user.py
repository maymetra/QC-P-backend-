# app/schemas/user.py
from pydantic import BaseModel

# Схема для создания нового пользователя (при регистрации)
# Ожидаем эти поля от фронтенда
class UserCreate(BaseModel):
    username: str
    password: str
    name: str
    role: str

# Схема для отображения пользователя
# Эти поля мы будем безопасно возвращать фронтенду (без пароля!)
class User(BaseModel):
    id: int
    username: str
    name: str
    role: str
    is_active: bool

    class Config:
        from_attributes = True # Позволяет Pydantic читать данные из ORM моделей