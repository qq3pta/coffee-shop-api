FROM python:3.12-slim

WORKDIR /app

RUN apt-get update \
 && apt-get install -y --no-install-recommends \
      curl \
      build-essential \
      sqlite3 \
 && rm -rf /var/lib/apt/lists/*

# Устанавливаем Poetry (последнюю версию)
RUN curl -sSL https://install.python-poetry.org | python3 - \
 && ln -s /root/.local/bin/poetry /usr/local/bin/poetry

# Копируем pyproject и ставим зависимости без dev-группы
COPY pyproject.toml poetry.lock ./
RUN poetry config virtualenvs.create false \
 && poetry install --no-interaction --no-root --without dev

# Копируем остальной код
COPY . .

EXPOSE 8000

CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]