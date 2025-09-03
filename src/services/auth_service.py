from uuid import UUID

from fastapi import HTTPException
from ..schemas.auth import UserCreate
from ..core.security import create_access_token
from ..repository.auth import AuthRepository  # type: ignore


class AuthService:

    def __init__(self):
        self.auth_repository = AuthRepository()

    async def register_new_user(self, user_data: UserCreate):
        db_user_by_username = await self.auth_repository.get_user_by_username(
            user_data.username
        )
        if db_user_by_username:
            raise HTTPException(status_code=400, detail="Username already registered")

        db_user_by_email = await self.auth_repository.get_user_by_email(user_data.email)
        if db_user_by_email:
            raise HTTPException(status_code=400, detail="Email already registered")

        db_user = await self.auth_repository.create_user(user_data)
        return db_user

    async def create_user_access_token(self, user_id: UUID, username: str):
        access_token = await create_access_token(
            data={"sub": str(user_id), "username": username}
        )
        return access_token
