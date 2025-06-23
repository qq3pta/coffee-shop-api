from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from typing import List
from app.schemas.user import UserRead, UserUpdate
from app.services.user import get_user, update_user, delete_user
from app.core.db import get_db
from app.services.auth import decode_token
from fastapi.security import OAuth2PasswordBearer

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/auth/login")
router = APIRouter()

async def get_current_user(token: str = Depends(oauth2_scheme), db: AsyncSession = Depends(get_db)):
    data = decode_token(token)
    return await get_user(data.user_id, db)

def admin_only(current_user=Depends(get_current_user)):
    if current_user.role != "admin":
        from fastapi import HTTPException, status
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Admins only")

@router.get("/me", response_model=UserRead)
async def read_me(current_user=Depends(get_current_user)):
    return current_user

@router.get("/", response_model=List[UserRead], dependencies=[Depends(admin_only)])
async def list_users(db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(User))
    return result.scalars().all()

@router.get("/{user_id}", response_model=UserRead, dependencies=[Depends(admin_only)])
async def read_user(user_id: int, db: AsyncSession = Depends(get_db)):
    return await get_user(user_id, db)

@router.patch("/{user_id}", response_model=UserRead, dependencies=[Depends(admin_only)])
async def edit_user(user_id: int, data: UserUpdate, db: AsyncSession = Depends(get_db)):
    return await update_user(user_id, data, db)

@router.delete("/{user_id}", status_code=204, dependencies=[Depends(admin_only)])
async def remove_user(user_id: int, db: AsyncSession = Depends(get_db)):
    await delete_user(user_id, db)