# app/main.py
from fastapi import FastAPI
from app.api.v1 import auth, projects # <-- Добавляем импорт projects

app = FastAPI(title="Quality Control API")

# Подключаем роутеры
app.include_router(auth.router, prefix="/api/v1")
app.include_router(projects.router, prefix="/api/v1") # <-- Добавляем роутер проектов


# Создаем первый "маршрут" или "эндпоинт"
@app.get("/")
def read_root():
    """Этот эндпоинт будет отвечать на запросы к главной странице API."""
    return {"message": "Welcome to Quality Control API!"}