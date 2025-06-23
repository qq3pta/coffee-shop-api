from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.ext.asyncio import AsyncSession
from app.schemas.user import UserCreate, VerifyRequest
from app.schemas.token import Token
from app.services.user import create_user, get_user_by_email, delete_unverified_users
from app.services.auth import verify_password, create_access_token, create_refresh_token, decode_token
from app.core.db import get_db

router = APIRouter()

@router.post("/signup", response_model=Token)
async def signup(data: UserCreate, db: AsyncSession = Depends(get_db)):
    user = await create_user(data, db)
    # здесь можно сгенерировать код и отправить по email/SMS (пока в консоль)
    return {
        "access_token": create_access_token(user.id),
        "refresh_token": create_refresh_token(user.id),
    }

@router.post("/login", response_model=Token)
async def login(form_data: OAuth2PasswordRequestForm = Depends(), db: AsyncSession = Depends(get_db)):
    user = await get_user_by_email(form_data.username, db)
    if not user or not verify_password(form_data.password, user.hashed_password):
        raise HTTPException(status_code=401, detail="Invalid credentials")
    return {
        "access_token": create_access_token(user.id),
        "refresh_token": create_refresh_token(user.id),
    }

@router.post("/refresh", response_model=Token)
async def refresh(token: str):
    data = decode_token(token)
    return {
        "access_token": create_access_token(data.user_id),
        "refresh_token": create_refresh_token(data.user_id),
    }

@router.post("/verify")
async def verify(data: VerifyRequest, db: AsyncSession = Depends(get_db)):
    # для упрощения: сразу отмечаем пользователя верифицированным
    q = await db.execute(select(User).filter_by(email=data.email))
    user = q.scalar_one_or_none()
    if not user:
        raise HTTPException(404, "User not found")
    user.is_verified = True
    db.add(user)
    await db.commit()
    return {"detail": "Verified"}