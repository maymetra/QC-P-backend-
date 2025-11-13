# app/schemas/project.py
from pydantic import BaseModel, constr
from .user import User
from typing import Optional
from datetime import date
from enum import Enum

# Создаем Enum для статусов
class ProjectStatus(str, Enum):
    in_progress = "in_progress"
    finished = "finished"
    on_hold = "on_hold"

# Базовая схема
class ProjectBase(BaseModel):
    name: constr(min_length=1, max_length=100)
    kunde: Optional[constr(max_length=100)] = None
    manager: Optional[constr(max_length=100)] = None
    # Убрали status отсюда, чтобы не делать его обязательным везде

# Схема для создания проекта (то, что мы ждем от фронтенда)
class ProjectCreate(ProjectBase):
    template: Optional[str] = None
    basePlannedDate: Optional[date] = None
    # Статус по умолчанию "in_progress"
    status: ProjectStatus = ProjectStatus.in_progress

# Схема для обновления проекта
class ProjectUpdate(BaseModel):
    name: Optional[constr(min_length=1, max_length=100)] = None
    kunde: Optional[constr(max_length=100)] = None
    manager: Optional[constr(max_length=100)] = None
    status: Optional[ProjectStatus] = None

# Простая схема
class ProjectSimple(BaseModel):
    id: int
    name: str

    class Config:
        from_attributes = True

# Основная схема для отображения
class Project(ProjectBase):
    id: int
    owner: User
    # Добавляем status сюда явно, так как убрали из Base
    status: ProjectStatus

    class Config:
        from_attributes = True