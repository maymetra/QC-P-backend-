# app/crud/crud_dashboard.py
from sqlalchemy.orm import Session
from sqlalchemy import func
from app.db import models
from datetime import date


def get_dashboard_stats(db: Session, user: models.User):
    """
    Получает статистику для дашборда.
    Админы и аудиторы видят статистику по всем проектам (кроме завершенных).
    """
    today = date.today()

    # 1. Базовый запрос: Присоединяем проекты и ИСКЛЮЧАЕМ завершенные
    items_query = db.query(models.Item).join(models.Project).filter(models.Project.status != 'finished')

    # Аудиторы и админы видят все, для менеджеров фильтруем по их имени
    if user.role not in ("admin", "auditor"):
        items_query = items_query.filter(models.Project.manager == user.name)

    # Задачи, ожидающие проверки
    pending_items = items_query.filter(models.Item.status == 'pending').all()

    # Просроченные открытые или отклоненные задачи
    overdue_items = items_query.filter(
        models.Item.planned_date < today,
        models.Item.status.in_(['open', 'rejected'])
    ).all()

    # --- 2. Подсчет для диаграммы ---
    # Начинаем запрос, сразу джойним проекты и фильтруем завершенные
    all_items_query = db.query(models.Item.status, func.count(models.Item.id)).join(models.Project).filter(models.Project.status != 'finished')

    # Если это не админ/аудитор, фильтруем по менеджеру
    if user.role not in ("admin", "auditor"):
        all_items_query = all_items_query.filter(models.Project.manager == user.name)

    status_counts_query = all_items_query.group_by(models.Item.status).all()

    # Инициализируем нули
    status_counts = {"open": 0, "approved": 0, "rejected": 0, "pending": 0}
    for status, count in status_counts_query:
        if status in status_counts:
            status_counts[status] = count

    return {
        "pending_items_count": len(pending_items),
        "overdue_items_count": len(overdue_items),
        "pending_items": pending_items,
        "overdue_items": overdue_items,
        "status_counts": status_counts
    }