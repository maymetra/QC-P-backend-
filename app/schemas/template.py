# app/schemas/template.py
from pydantic import BaseModel
from typing import List

# Базовая схема
class TemplateBase(BaseModel):
    name: str
    items: List[str]

# Схема для создания (то, что приходит от фронтенда)
class TemplateCreate(TemplateBase):
    pass

# Схема для отображения (то, что мы отдаем фронтенду)
class Template(TemplateBase):
    id: int
    owner_id: int

    class Config:
        from_attributes = True