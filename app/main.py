# app/main.py
import os
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.api.v1 import auth, projects, users, items, templates, knowledge_base, dashboard, files

app = FastAPI(title="Quality Control API")

# Получаем список разрешенных origins из переменной окружения
# Переменная должна содержать адреса через запятую, например: "http://localhost:5173,http://gema-qmc01l.dcm.psigem.de"
origins = os.environ.get("ALLOWED_ORIGINS", "http://localhost:5173,http://127.0.0.1:5173").split(",")


app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# Подключаем роутеры
app.include_router(auth.router, prefix="/api/v1")
app.include_router(projects.router, prefix="/api/v1")
app.include_router(users.router, prefix="/api/v1")
app.include_router(items.router, prefix="/api/v1")
app.include_router(templates.router, prefix="/api/v1")
app.include_router(knowledge_base.router, prefix="/api/v1")
app.include_router(dashboard.router, prefix="/api/v1")
app.include_router(files.router, prefix="/api/v1")



# Создаем первый "маршрут" или "эндпоинт"
@app.get("/")
def read_root():
    """Этот эндпоинт будет отвечать на запросы к главной странице API."""
    return {"message": "Welcome to Quality Control API!"}