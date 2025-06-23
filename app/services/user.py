from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from fastapi import HTTPException, status
from app.models.user import User, RoleEnum
from app.schemas.user import UserCreate, UserUpdate
from app.services.auth import hash_password
from datetime import datetime, timedelta

async def create_user(user_in: UserCreate, db: AsyncSession) -> User:
    q = await db.execute(select(User).filter_by(email=user_in.email))
    if q.scalar_one_or_none():
        raise HTTPException(status_code=400, detail="Email already registered")
    user = User(
        email=user_in.email,
        hashed_password=hash_password(user_in.password),
        first_name=user_in.first_name,
        last_name=user_in.last_name,
    )
    db.add(user)
    await db.commit()
    await db.refresh(user)
    return user

async def get_user_by_email(email: str, db: AsyncSession) -> User | None:
    q = await db.execute(select(User).filter_by(email=email))
    return q.scalar_one_or_none()

async def get_user(user_id: int, db: AsyncSession) -> User:
    q = await db.execute(select(User).filter_by(id=user_id))
    user = q.scalar_one_or_none()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    return user

async def update_user(user_id: int, data: UserUpdate, db: AsyncSession) -> User:
    user = await get_user(user_id, db)
    for field, value in data:
        setattr(user, field, value)
    db.add(user)
    await db.commit()
    await db.refresh(user)
    return user

async def delete_user(user_id: int, db: AsyncSession):
    user = await get_user(user_id, db)
    await db.delete(user)
    await db.commit()

async def delete_unverified_users(db: AsyncSession):
    threshold = datetime.utcnow() - timedelta(days=2)
    q = await db.execute(select(User).filter(User.is_verified == False, User.created_at < threshold))
    for user in q.scalars().all():
        await db.delete(user)
    await db.commit()