# app/schemas/item.py
from pydantic import BaseModel
from datetime import date
from typing import List, Any
from .project import ProjectSimple

# Эта схема описывает структуру одного документа или вложения
class Attachment(BaseModel):
    uid: str
    name: str
    url: str

# Базовая схема для Item
class ItemBase(BaseModel):
    item: str
    action: str | None = None
    author: str | None = None
    reviewer: str | None = None
    planned_date: date | None = None
    closed_date: date | None = None
    status: str = "open"
    comment: str | None = None
    documents: List[Any] = [] # Используем Any, т.к. структура может быть разной
    attachments: List[Any] = []

# Схема для создания Item
class ItemCreate(ItemBase):
    pass

# Схема для обновления Item
class ItemUpdate(BaseModel):
    item: str | None = None
    action: str | None = None
    author: str | None = None
    reviewer: str | None = None
    planned_date: date | None = None
    closed_date: date | None = None
    status: str | None = None
    comment: str | None = None
    documents: List[Any] | None = None
    attachments: List[Any] | None = None

# Схема для отображения Item в API
class Item(ItemBase):
    id: int
    project_id: int
    project: ProjectSimple

    class Config:
        from_attributes = True