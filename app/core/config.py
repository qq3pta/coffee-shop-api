from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    """
    Application settings, загружаются из .env
    """

    PROJECT_NAME: str = "Coffee Shop API"


    DATABASE_URL: str = "sqlite+aiosqlite:///./db.sqlite3"
    SECRET_KEY: str
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30
    REFRESH_TOKEN_EXPIRE_MINUTES: int = 1440

    REDIS_URL: str
    SMTP_HOST: str
    SMTP_PORT: int
    SMTP_USER: str
    SMTP_PASS: str

    class Config:
        env_file = ".env"


settings = Settings()