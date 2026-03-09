FROM python:3.12-slim

WORKDIR /app

# системные зависимости (ВАЖНО для сборки пакетов)
RUN apt-get update && apt-get install -y \
    build-essential \
    curl \
    && rm -rf /var/lib/apt/lists/*

# обновляем pip заранее (критично)
RUN pip install --upgrade pip

# ставим poetry
RUN pip install poetry

# копируем зависимости
COPY pyproject.toml poetry.lock ./

# отключаем venv и ставим зависимости
RUN poetry config virtualenvs.create false \
    && poetry install --no-interaction --no-ansi --no-root

# копируем код
COPY . .

# запуск
CMD alembic upgrade head && uvicorn src.main:app --host 0.0.0.0 --port 8000