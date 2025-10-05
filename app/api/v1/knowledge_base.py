# app/api/v1/knowledge_base.py
from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from typing import List

from app.db import models
from app.db.session import get_db
from app.schemas import knowledge_base as kb_schema
from app.crud import crud_knowledge_base
from app.api import deps

router = APIRouter(prefix="/knowledge-base", tags=["Knowledge Base"])

@router.get("/", response_model=List[kb_schema.KnowledgeBaseItem])
def read_knowledge_base(
    db: Session = Depends(get_db),
    current_user: models.User = Depends(deps.get_current_user)
):
    """
    Получить все элементы из базы знаний.
    """
    items = crud_knowledge_base.get_all_items(db)
    return items