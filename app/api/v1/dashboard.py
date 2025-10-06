# app/api/v1/dashboard.py
from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.db import models
from app.db.session import get_db
from app.schemas import dashboard as dashboard_schema
from app.crud import crud_dashboard
from app.api import deps

router = APIRouter(prefix="/dashboard", tags=["Dashboard"])

@router.get("/statistics", response_model=dashboard_schema.DashboardStats)
def read_dashboard_statistics(
    db: Session = Depends(get_db),
    current_user: models.User = Depends(deps.get_current_auditor_or_admin_user)
):
    """
    Получить статистику для дашборда. 
    Доступно только для администраторов и аудиторов.
    """
    stats = crud_dashboard.get_dashboard_stats(db, user=current_user)
    return stats