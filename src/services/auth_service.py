from fastapi import HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from src.schemas.auth import UserCreate
from src.repository import auth as auth_repository
from src.core.security import create_access_token


async def register_new_user(db: AsyncSession, user_data: UserCreate):
    db_user_by_username = await auth_repository.get_user_by_username(
        db, user_data.username
    )
    if db_user_by_username:
        raise HTTPException(status_code=400, detail="Username already registered")

    db_user_by_email = await auth_repository.get_user_by_email(db, user_data.email)
    if db_user_by_email:
        raise HTTPException(status_code=400, detail="Email already registered")

    db_user = await auth_repository.create_user(db, user_data)
    return db_user


async def create_user_access_token(username: str):
    access_token = create_access_token(data={"sub": username})
    return {"access_token": access_token, "token_type": "bearer"}
