# app/db/models.py
# (импорты sqlalchemy остаются те же, добавляем ForeignKey и relationship)
from sqlalchemy import Column, Integer, String, Boolean, ForeignKey, Date, JSON
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


class Project(Base):
    __tablename__ = "projects"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, index=True, nullable=False)
    kunde = Column(String)
    manager = Column(String)
    status = Column(String, nullable=False)

    # Связь с таблицей users. Указываем, что это "внешний ключ"
    owner_id = Column(Integer, ForeignKey("users.id"))
    owner = relationship("User", back_populates="projects")

    # Обратная связь, чтобы у проекта можно было получить список его items
    items = relationship("Item", back_populates="project", cascade="all, delete-orphan")


class Item(Base):
    __tablename__ = "items"

    id = Column(Integer, primary_key=True, index=True)
    item = Column(String, nullable=False)
    action = Column(String)
    author = Column(String)
    reviewer = Column(String)
    planned_date = Column(Date)
    closed_date = Column(Date)
    status = Column(String, nullable=False, default="open")
    comment = Column(String)

    # Мы будем хранить документы и вложения как JSON-массивы.
    # Это просто и эффективно для нашей задачи.
    documents = Column(JSON)
    attachments = Column(JSON)

    # Связь с таблицей projects
    project_id = Column(Integer, ForeignKey("projects.id"))
    project = relationship("Project", back_populates="items")


class Template(Base):
    __tablename__ = "templates"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, unique=True, index=True, nullable=False)
    items = Column(JSON, nullable=False)

    # Связь с пользователем, который создал шаблон (опционально, но хорошая практика)
    owner_id = Column(Integer, ForeignKey("users.id"))
    owner = relationship("User")

class KnowledgeBaseItem(Base):
    __tablename__ = "knowledge_base_items"

    id = Column(Integer, primary_key=True, index=True)
    category = Column(String, index=True, nullable=False)
    item = Column(String, nullable=False, unique=True)