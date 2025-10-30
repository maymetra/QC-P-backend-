# Шаг 1: Используем официальный образ Python
FROM python:3.12-slim

# Шаг 2: Устанавливаем системные зависимости, необходимые для сборки пакетов
RUN apt-get update && apt-get install -y build-essential

# Шаг 3: Устанавливаем рабочую директорию
WORKDIR /app

# Шаг 4: Копируем файлы с зависимостями
COPY pyproject.toml poetry.lock ./

# Шаг 5: Устанавливаем Poetry и зависимости проекта
RUN pip install poetry && \
    poetry config virtualenvs.create false && \
    poetry install --without dev --no-interaction --no-ansi --no-root

# Шаг 6: Копируем весь остальной код приложения
COPY . .

# Шаг 7: Указываем команду для запуска
CMD ["gunicorn", "app.main:app", "--workers", "4", "--worker-class", "uvicorn.workers.UvicornWorker", "--bind", "0.0.0.0:8000"]