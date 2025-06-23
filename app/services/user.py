from typing import List, Optional
from datetime import datetime, timedelta

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from fastapi import HTTPException, status

from app.models.user import User
from app.schemas.user import UserCreate, UserUpdate
from app.services.auth import hash_password
import uuid


async def create_user(user_in: UserCreate, db: AsyncSession) -> User:
    """
    Создаёт нового пользователя, проверяя уникальность email и создаёт код верификации.
    """
    q = await db.execute(select(User).filter_by(email=user_in.email))
    if q.scalar_one_or_none():
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST,
                            detail="Email already registered")

    # Генерируем код и срок действия
    code = str(uuid.uuid4())
    expiry = datetime.utcnow() + timedelta(days=2)

    user = User(
        email=user_in.email,
        hashed_password=hash_password(user_in.password),
        first_name=user_in.first_name,
        last_name=user_in.last_name,
        verification_code=code,
        verification_expiry=expiry,
    )
    db.add(user)
    await db.commit()
    await db.refresh(user)
    return user

async def get_user_by_email(email: str, db: AsyncSession) -> Optional[User]:
    """
    Возвращает пользователя по email или None.
    """
    q = await db.execute(select(User).filter_by(email=email))
    return q.scalar_one_or_none()


async def get_user(user_id: int, db: AsyncSession) -> User:
    """
    Возвращает пользователя по ID или кидает 404.
    """
    q = await db.execute(select(User).filter_by(id=user_id))
    user = q.scalar_one_or_none()
    if not user:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                            detail="User not found")
    return user

async def get_users(db: AsyncSession) -> List[User]:
    """
    Возвращает список всех пользователей.
    """
    q = await db.execute(select(User))
    return q.scalars().all()

async def update_user(user_id: int, data: UserUpdate, db: AsyncSession) -> User:
    """
    Частично обновляет данные пользователя.
    """
    user = await get_user(user_id, db)
    update_data = data.dict(exclude_unset=True)
    for field, value in update_data.items():
        setattr(user, field, value)

    db.add(user)
    await db.commit()
    await db.refresh(user)
    return user

async def delete_user(user_id: int, db: AsyncSession) -> bool:
    """
    Удаляет пользователя и возвращает True, если всё прошло ок.
    """
    q = await db.execute(select(User).filter_by(id=user_id))
    user = q.scalar_one_or_none()
    if not user:
        return False

    await db.delete(user)
    await db.commit()
    return True

async def delete_unverified_users(db: AsyncSession) -> None:
    """
    Удаляет всех пользователей, не прошедших верификацию за 2 дня.
    """
    threshold = datetime.utcnow() - timedelta(days=2)
    q = await db.execute(
        select(User).filter(
            User.is_verified == False,
            User.created_at < threshold
        )
    )
    for user in q.scalars().all():
        await db.delete(user)
    await db.commit()
