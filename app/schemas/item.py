# app/schemas/item.py
from pydantic import BaseModel
from datetime import date
from typing import List, Any
from .project import ProjectSimple

# Обновляем эту схему
class Attachment(BaseModel):
    uid: str      # Уникальный ID файла (генерируется фронтендом или сервером)
    name: str     # Оригинальное имя файла
    file_path: str # Путь на сервере/уникальное имя

# В ItemBase и ItemUpdate меняем List[Any] на List[Attachment]
class ItemBase(BaseModel):
    item: str
    action: str | None = None
    author: str | None = None
    reviewer: str | None = None
    planned_date: date | None = None
    closed_date: date | None = None
    status: str = "open"
    comment: str | None = None
    documents: List[Attachment] = []
    attachments: List[Attachment] = []

class ItemCreate(ItemBase):
    pass

class ItemUpdate(BaseModel):
    item: str | None = None
    action: str | None = None
    author: str | None = None
    reviewer: str | None = None
    planned_date: date | None = None
    closed_date: date | None = None
    status: str | None = None
    comment: str | None = None
    documents: List[Attachment] | None = None
    attachments: List[Attachment] | None = None

# Схема для отображения Item в API
class Item(ItemBase):
    id: int
    project_id: int
    project: ProjectSimple

    class Config:
        from_attributes = True