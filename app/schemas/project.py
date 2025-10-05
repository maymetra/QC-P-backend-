# app/schemas/project.py
from pydantic import BaseModel
from .user import User  # <-- 1. Импортируем схему пользователя
from typing import Optional  # <-- Импортируем Optional
from datetime import date     # <-- Импортируем date

# Базовая схема, содержит общие поля
class ProjectBase(BaseModel):
    name: str
    kunde: str | None = None
    manager: str | None = None
    status: str

# Схема для создания проекта (то, что мы ждем от фронтенда)
class ProjectCreate(ProjectBase):
    template: Optional[str] = None
    basePlannedDate: Optional[date] = None

# Схема для обновления проекта
class ProjectUpdate(ProjectBase):
    pass

# Основная схема для отображения проекта (то, что мы отдаем фронтенду)
class Project(ProjectBase):
    id: int

    owner: User  # <-- 3. ДОБАВЛЯЕМ это поле. Оно будет содержать вложенный объект пользователя

    class Config:
        from_attributes = True