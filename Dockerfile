# --- ЭТАП 1: Установка зависимостей ---
FROM python:3.12-slim as builder

RUN apt-get update && apt-get install -y build-essential

WORKDIR /app

RUN pip install poetry

COPY poetry.lock pyproject.toml ./

# ▼▼▼ ДОБАВЛЕНО ИЗМЕНЕНИЕ ▼▼▼
# Эта команда говорит Poetry создавать папку .venv внутри текущей директории (/app)
RUN poetry config virtualenvs.in-project true

# Теперь poetry install создаст .venv прямо здесь
RUN poetry install --without dev --no-interaction --no-ansi --no-root

# --- ЭТАП 2: Сборка финального образа ---
FROM python:3.12-slim

WORKDIR /app

# Теперь эта команда сработает, так как .venv будет на месте
COPY --from=builder /app/.venv /app/.venv

ENV PATH="/app/.venv/bin:$PATH"

COPY . .

CMD ["gunicorn", "app.main:app", "--workers", "4", "--worker-class", "uvicorn.workers.UvicornWorker", "--bind", "0.0.0.0:8000"]