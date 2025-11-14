# app/schemas/history.py
from pydantic import BaseModel
from datetime import datetime

class ProjectHistoryEventBase(BaseModel):
    user_name: str
    event_type: str
    details: str | None = None

class ProjectHistoryEvent(ProjectHistoryEventBase):
    id: int
    timestamp: datetime
    project_id: int

    class Config:
        from_attributes = True