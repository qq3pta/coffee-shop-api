# Coffee Shop API

**Block:** User management  
**Tech stack:** FastAPI, SQLAlchemy, Alembic, Celery, SQLite, Docker

## Быстрый старт

1. Скопировать `.env.sample` → `.env` и заполнить.
2. `poetry install`
3. `docker-compose up --build`
4. `docker-compose exec web alembic upgrade head`
5. Открыть `http://localhost:8000/docs`
