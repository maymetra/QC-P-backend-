# app/main.py
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.api.v1 import auth, projects, users, items

app = FastAPI(title="Quality Control API")

# Список адресов, с которых мы разрешаем запросы.
# В будущем сюда можно будет добавить адрес твоего продакшн-сайта.
origins = [
    "http://localhost:5173", # Адрес твоего React-приложения
    "http://127.0.0.1:5173",
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,  # Разрешить запросы с этих адресов
    allow_credentials=True, # Разрешить передачу cookie/токенов
    allow_methods=["*"],    # Разрешить все методы (GET, POST, etc.)
    allow_headers=["*"],    # Разрешить все заголовки
)


# Подключаем роутеры
app.include_router(auth.router, prefix="/api/v1")
app.include_router(projects.router, prefix="/api/v1")
app.include_router(users.router, prefix="/api/v1")
app.include_router(items.router, prefix="/api/v1")

# Создаем первый "маршрут" или "эндпоинт"
@app.get("/")
def read_root():
    """Этот эндпоинт будет отвечать на запросы к главной странице API."""
    return {"message": "Welcome to Quality Control API!"}