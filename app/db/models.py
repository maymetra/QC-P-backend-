# app/db/models.py
# (импорты sqlalchemy остаются те же, добавляем ForeignKey и relationship)
from sqlalchemy import Column, Integer, String, Boolean, ForeignKey
from sqlalchemy.orm import relationship
from .base import Base


class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    username = Column(String, unique=True, index=True, nullable=False)
    name = Column(String, nullable=False)
    hashed_password = Column(String, nullable=False)
    role = Column(String, nullable=False)
    is_active = Column(Boolean(), default=True)

    # Добавляем "обратную" связь, чтобы у пользователя можно было получить его проекты
    projects = relationship("Project", back_populates="owner")


# --- НАЧАЛО НОВОГО КОДА ---
class Project(Base):
    __tablename__ = "projects"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, index=True, nullable=False)
    kunde = Column(String)
    manager = Column(String)
    status = Column(String, nullable=False)

    # Связь с таблицей users. Указываем, что это "внешний ключ"
    owner_id = Column(Integer, ForeignKey("users.id"))

    # Создаем "виртуальное" поле, которое SQLAlchemy будет автоматически
    # заполнять данными пользователя-владельца
    owner = relationship("User", back_populates="projects")
# --- КОНЕЦ НОВОГО КОДА ---