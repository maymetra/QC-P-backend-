# app/schemas/knowledge_base.py
from pydantic import BaseModel

# Схема для одного элемента базы знаний
class KnowledgeBaseItem(BaseModel):
    id: int
    category: str
    item: str

    class Config:
        from_attributes = True

# Схема для сгруппированного ответа
class KnowledgeBaseCategory(BaseModel):
    category: str
    items: list[str]