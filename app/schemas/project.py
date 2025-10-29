# app/schemas/project.py
from pydantic import BaseModel, constr
from .user import User
from typing import Optional
from datetime import date
from enum import Enum

# Создаем Enum для статусов, чтобы принимать только разрешенные значения
class ProjectStatus(str, Enum):
    in_progress = "in_progress"
    finished = "finished"
    on_hold = "on_hold"

# Базовая схема, содержит общие поля
class ProjectBase(BaseModel):
    name: constr(min_length=1, max_length=100) # Ограничиваем длину имени
    kunde: Optional[constr(max_length=100)] = None
    manager: Optional[constr(max_length=100)] = None
    status: ProjectStatus # Теперь здесь можно использовать только значения из Enum

# Схема для создания проекта (то, что мы ждем от фронтенда)
class ProjectCreate(ProjectBase):
    template: Optional[str] = None
    basePlannedDate: Optional[date] = None

# Схема для обновления проекта
class ProjectUpdate(BaseModel): # Меняем наследование, чтобы разрешить частичное обновление
    name: Optional[constr(min_length=1, max_length=100)] = None
    kunde: Optional[constr(max_length=100)] = None
    manager: Optional[constr(max_length=100)] = None
    status: Optional[ProjectStatus] = None


# Простая схема для вложения в другие схемы (например, в Item)
class ProjectSimple(BaseModel):
    id: int
    name: str

    class Config:
        from_attributes = True

# Основная схема для отображения проекта (то, что мы отдаем фронтенду)
class Project(ProjectBase):
    id: int
    owner: User

    class Config:
        from_attributes = True