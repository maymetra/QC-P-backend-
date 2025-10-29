# Шаг 1: Используем официальный легковесный образ Python
FROM python:3.12-slim

# Шаг 2: Устанавливаем рабочую директорию
WORKDIR /app

# Шаг 3: Копируем скачанные пакеты и файл с требованиями
COPY requirements.txt .
COPY packages/ /app/packages/

# Шаг 4: Устанавливаем зависимости из локальной папки, без обращения к сети
RUN pip install --no-index --find-links=/app/packages -r requirements.txt

# Шаг 5: Копируем остальной код приложения
COPY . .

# Шаг 6: Указываем команду для запуска
CMD ["gunicorn", "app.main:app", "--workers", "4", "--worker-class", "uvicorn.workers.UvicornWorker", "--bind", "0.0.0.0:8000"]