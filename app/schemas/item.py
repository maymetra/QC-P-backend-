# app/schemas/item.py
from pydantic import BaseModel, constr
from datetime import date
from typing import List, Any, Optional
from .project import ProjectSimple
from enum import Enum

# Enum для статусов задач
class ItemStatus(str, Enum):
    open = "open"
    pending = "pending"
    approved = "approved"
    rejected = "rejected"

class Attachment(BaseModel):
    uid: str
    name: str
    file_path: str

class ItemBase(BaseModel):
    item: constr(min_length=1, max_length=255)
    action: Optional[constr(max_length=1000)] = None
    author: Optional[constr(max_length=100)] = None
    reviewer: Optional[constr(max_length=100)] = None
    planned_date: Optional[date] = None
    closed_date: Optional[date] = None
    status: ItemStatus = ItemStatus.open
    comment: Optional[constr(max_length=2000)] = None
    documents: List[Attachment] = []
    attachments: List[Attachment] = []

class ItemCreate(ItemBase):
    pass

class ItemUpdate(BaseModel):
    item: Optional[constr(min_length=1, max_length=255)] = None
    action: Optional[constr(max_length=1000)] = None
    author: Optional[constr(max_length=100)] = None
    reviewer: Optional[constr(max_length=100)] = None
    planned_date: Optional[date] = None
    closed_date: Optional[date] = None
    status: Optional[ItemStatus] = None
    comment: Optional[constr(max_length=2000)] = None
    documents: Optional[List[Attachment]] = None
    attachments: Optional[List[Attachment]] = None

class Item(ItemBase):
    id: int
    project_id: int
    project: ProjectSimple

    class Config:
        from_attributes = True