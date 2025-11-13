# app/schemas/dashboard.py
from pydantic import BaseModel
from typing import List, Dict
from .item import Item

class DashboardStats(BaseModel):
    pending_items_count: int
    overdue_items_count: int
    pending_items: List[Item]
    overdue_items: List[Item]
    status_counts: Dict[str, int] # <-- ДОБАВЛЕНО