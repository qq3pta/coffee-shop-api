from fastapi import FastAPI
from app.core.config import settings
from app.routers import auth, users

app = FastAPI(title=settings.PROJECT_NAME)

app.include_router(auth.router, prefix="/auth", tags=["auth"])
app.include_router(users.router, prefix="/users", tags=["users"])