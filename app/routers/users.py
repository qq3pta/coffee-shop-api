from typing import List

from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select

from app.models.user import User
from app.schemas.user import UserRead, UserUpdate
from app.services.user import get_user, get_users, update_user, delete_user
from app.services.auth import decode_token
from app.core.db import get_db

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/auth/login")

router = APIRouter(
    prefix="/users",
    tags=["users"],
)


async def get_current_user(token: str = Depends(oauth2_scheme), db: AsyncSession = Depends(get_db)) -> User:
    data = decode_token(token)
    user = await get_user(data.user_id, db)
    if not user:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid credentials")
    return user


def admin_only(current_user: User = Depends(get_current_user)) -> User:
    if current_user.role != "admin":
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Admin privileges required")
    return current_user


@router.get("/me", response_model=UserRead, summary="Get current authenticated user")
async def read_me(current_user: User = Depends(get_current_user)):
    return current_user


@router.get("/", response_model=List[UserRead], summary="List all users (admin only)")
async def read_users(
    db: AsyncSession = Depends(get_db),
    _=Depends(admin_only),
):
    result = await db.execute(select(User))
    users = result.scalars().all()
    return users


@router.get("/{user_id}", response_model=UserRead, summary="Get user by ID (admin only)")
async def read_user(
    user_id: int,
    db: AsyncSession = Depends(get_db),
    _=Depends(admin_only),
):
    user = await get_user(user_id, db)
    if not user:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")
    return user


@router.patch("/{user_id}", response_model=UserRead, summary="Update user (admin only)")
async def patch_user(
    user_id: int,
    user_data: UserUpdate,
    db: AsyncSession = Depends(get_db),
    _=Depends(admin_only),
):
    updated = await update_user(user_id, user_data, db)
    if not updated:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found or nothing to update")
    return updated


@router.delete("/{user_id}", status_code=status.HTTP_204_NO_CONTENT, summary="Delete user (admin only)")
async def remove_user(
    user_id: int,
    db: AsyncSession = Depends(get_db),
    _=Depends(admin_only),
):
    success = await delete_user(user_id, db)
    if not success:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")
    return None