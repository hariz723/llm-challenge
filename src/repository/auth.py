from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from src.models.auth import User
from src.schemas.auth import UserCreate
from src.core.security import hash_password


async def get_user_by_username(db: AsyncSession, username: str):
    result = await db.execute(select(User).filter(User.username == username))
    return result.scalars().first()


async def get_user_by_email(db: AsyncSession, email: str):
    result = await db.execute(select(User).filter(User.email == email))
    return result.scalars().first()


async def create_user(db: AsyncSession, user: UserCreate):
    hashed_password = await hash_password(user.password)
    db_user = User(
        username=user.username, email=user.email, hashed_password=hashed_password
    )
    db.add(db_user)
    await db.commit()
    await db.refresh(db_user)
    return db_user
