# app/schemas/dashboard.py
from pydantic import BaseModel
from typing import List
from .item import Item  # Импортируем существующую схему Item

class DashboardStats(BaseModel):
    pending_items_count: int
    overdue_items_count: int
    pending_items: List[Item]
    overdue_items: List[Item]