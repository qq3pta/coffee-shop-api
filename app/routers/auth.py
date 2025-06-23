from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select

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

router = APIRouter(prefix="/auth", tags=["auth"])


@router.post("/signup", response_model=Token, summary="Register new user")
async def signup(data: UserCreate, db: AsyncSession = Depends(get_db)):
    # Создаём пользователя
    user = await create_user(data, db)
    # По желанию: здесь можно вызвать delete_unverified_users(db)
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


@router.post("/verify", summary="Verify user (email/SMS)")
async def verify(data: VerifyRequest, db: AsyncSession = Depends(get_db)):
    # Упрощённо: сразу помечаем пользователя верифицированным
    result = await db.execute(select(User).filter_by(email=data.email))
    user = result.scalar_one_or_none()
    if not user:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")
    user.is_verified = True
    db.add(user)
    await db.commit()
    return {"detail": "User verified"}