from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    """
    Application settings, загружаются из .env
    """

    # Если хотите задать дефолтный SQLite URL,
    # используйте оператор = и обрамите строку в кавычки:
    DATABASE_URL: str = "sqlite+aiosqlite:///./db.sqlite3"
    SECRET_KEY: str               # обязательно задаётся в .env
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30
    REFRESH_TOKEN_EXPIRE_MINUTES: int = 1440

    # Для Redis, Mail и т.п. — без дефолтов, все из .env
    REDIS_URL: str
    SMTP_HOST: str
    SMTP_PORT: int
    SMTP_USER: str
    SMTP_PASS: str

    class Config:
        env_file = ".env"


settings = Settings()