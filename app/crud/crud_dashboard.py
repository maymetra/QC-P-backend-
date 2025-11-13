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

    # --- НОВЫЙ КОД: Подсчет всех статусов ---
    all_items_query = db.query(models.Item.status, func.count(models.Item.id))

    # Если это не админ/аудитор, фильтруем и этот запрос
    if user.role not in ("admin", "auditor"):
        all_items_query = all_items_query.join(models.Project).filter(models.Project.manager == user.name)

    status_counts_query = all_items_query.group_by(models.Item.status).all()

    # Инициализируем нули, чтобы на фронтенде всегда были все ключи
    status_counts = {"open": 0, "approved": 0, "rejected": 0, "pending": 0}
    for status, count in status_counts_query:
        if status in status_counts:
            status_counts[status] = count
    # --- КОНЕЦ НОВОГО КОДА ---

    return {
        "pending_items_count": len(pending_items),
        "overdue_items_count": len(overdue_items),
        "pending_items": pending_items,
        "overdue_items": overdue_items,
        "status_counts": status_counts  # <-- НАШИ НОВЫЕ ДАННЫЕ
    }