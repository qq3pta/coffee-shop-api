# Coffee Shop API

**Block:** User management  
**Tech stack:** FastAPI, SQLAlchemy, Alembic, Celery, SQLite, Docker

## Quick Start

1. Copy `.env.sample` → `.env` and fill in required values
2. `poetry install`
3. `docker-compose up --build`
4. `docker-compose exec web alembic upgrade head`
5. Open `http://localhost:8000/docs`
