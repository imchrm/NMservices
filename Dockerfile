FROM python:3.11-slim AS base

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1

WORKDIR /app

RUN pip install --no-cache-dir poetry==2.1.1 && \
    poetry config virtualenvs.create false

COPY pyproject.toml poetry.lock ./
RUN poetry install --no-interaction --no-ansi --only main

COPY alembic.ini ./
COPY alembic/ ./alembic/
COPY src/ ./src/

ENV ENVIRONMENT=production

EXPOSE 8000

CMD ["uvicorn", "nms.main:app", "--host", "0.0.0.0", "--port", "8000", "--app-dir", "src"]
