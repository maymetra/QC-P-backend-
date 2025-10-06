# app/crud/crud_dashboard.py
from sqlalchemy.orm import Session
from sqlalchemy import func
from app.db import models
from datetime import date


def get_dashboard_stats(db: Session, user: models.User):
    """
    Получает статистику для дашборда.
    Админы и аудиторы видят статистику по всем проектам.
    """
    today = date.today()

    # Базовый запрос к задачам (items)
    items_query = db.query(models.Item).join(models.Project)

    # Аудиторы и админы видят все, для других ролей (если появятся) можно добавить фильтры
    if user.role not in ("admin", "auditor"):
        # Для менеджера можно было бы добавить фильтр по его проектам,
        # но т.к. дашборд только для админов/аудиторов, оставляем так.
        items_query = items_query.filter(models.Project.manager == user.name)

    # Задачи, ожидающие проверки
    pending_items = items_query.filter(models.Item.status == 'pending').all()

    # Просроченные открытые или отклоненные задачи
    overdue_items = items_query.filter(
        models.Item.planned_date < today,
        models.Item.status.in_(['open', 'rejected'])
    ).all()

    return {
        "pending_items_count": len(pending_items),
        "overdue_items_count": len(overdue_items),
        "pending_items": pending_items,
        "overdue_items": overdue_items,
    }