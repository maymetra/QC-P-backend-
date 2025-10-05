# app/db/session.py
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from app.core.config import settings

# Создаем "движок" для подключения к нашей базе данных
engine = create_engine(settings.DATABASE_URL)

# Создаем "фабрику" сессий, которая будет создавать новые сессии по запросу
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

def get_db():
    """
    Функция-зависимость (dependency), которую FastAPI будет вызывать
    для каждого запроса. Она создает сессию, отдает ее в эндпоинт
    и гарантированно закрывает после выполнения.
    """
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()