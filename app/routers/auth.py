from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from datetime import datetime

from app.models.user import User
from app.schemas.user import UserCreate, VerifyRequest
from app.schemas.token import Token
from app.services.user import create_user, get_user_by_email
from app.services.auth import (
    verify_password,
    create_access_token,
    create_refresh_token,
    decode_token,
)
from app.core.db import get_db
from app.tasks.worker import send_verification_email_task

router = APIRouter(tags=["auth"])


@router.post("/signup", response_model=Token, summary="Register new user")
async def signup(data: UserCreate, db: AsyncSession = Depends(get_db)):
    # создаём пользователя и код верификации в сервисе
    user = await create_user(data, db)
    # запускаем фоновую отправку письма
    send_verification_email_task.delay(user.email, user.verification_code)
    return {
        "access_token": create_access_token(user.id),
        "refresh_token": create_refresh_token(user.id),
        "token_type": "bearer",
    }


@router.post("/login", response_model=Token, summary="Authenticate and get tokens")
async def login(
    form_data: OAuth2PasswordRequestForm = Depends(),
    db: AsyncSession = Depends(get_db),
):
    user = await get_user_by_email(form_data.username, db)
    if not user or not verify_password(form_data.password, user.hashed_password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid credentials",
            headers={"WWW-Authenticate": "Bearer"},
        )
    return {
        "access_token": create_access_token(user.id),
        "refresh_token": create_refresh_token(user.id),
        "token_type": "bearer",
    }


@router.post("/refresh", response_model=Token, summary="Refresh access token")
async def refresh(token: str):
    data = decode_token(token)
    return {
        "access_token": create_access_token(data.user_id),
        "refresh_token": create_refresh_token(data.user_id),
        "token_type": "bearer",
    }


@router.post("/verify", summary="Verify user by code")
async def verify(data: VerifyRequest, db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(User).filter_by(email=data.email))
    user = result.scalar_one_or_none()
    if not user:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")
    # проверяем код и срок действия
    if user.verification_code != data.code or user.verification_expiry < datetime.utcnow():
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Invalid or expired code")
    user.is_verified = True
    user.verification_code = None
    user.verification_expiry = None
    db.add(user)
    await db.commit()
    return {"detail": "User verified"}
