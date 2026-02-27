FROM python:3.12-slim

ENV PYTHONUNBUFFERED=1

WORKDIR /app

RUN apt-get update && apt-get install -y \
    build-essential \
    libpq-dev \
    && rm -rf /var/lib/apt/lists/*

COPY pyproject.toml poetry.lock ./
COPY src ./src
COPY README.md ./

RUN pip install --upgrade pip poetry \
    && poetry config virtualenvs.create false \
    && poetry install --only main --no-interaction --no-ansi

ENV PYTHONPATH="/app:${PYTHONPATH}"

CMD ["gunicorn", "products.main:app", \
     "-k", "uvicorn.workers.UvicornWorker", \
     "--workers", "4", \
     "--bind", "0.0.0.0:7000"]
