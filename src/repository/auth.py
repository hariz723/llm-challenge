from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from ..models.auth import User
from ..schemas.auth import UserCreate
from ..core.security import hash_password


class AuthRepository:

    def __init__(self):
        self.db = AsyncSession

    async def get_user_by_username(self, username: str):
        result = await self.db.execute(select(User).filter(User.username == username))
        return result.scalars().first()

    async def get_user_by_email(self, email: str):
        result = await self.db.execute(select(User).filter(User.email == email))
        return result.scalars().first()

    async def create_user(self, user: UserCreate):

        hashed_password = await hash_password(user.password)
        db_user = User(
            username=user.username, email=user.email, hashed_password=hashed_password
        )
        self.db.add(db_user)
        await self.db.commit()
        await self.db.refresh(db_user)
        return db_user
