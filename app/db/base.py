# app/db/base.py
from sqlalchemy.orm import declarative_base

# Это базовый класс, от которого будут наследоваться все наши модели (таблицы)
Base = declarative_base()