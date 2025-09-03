from fastapi import Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
import jwt
from ..models.database import get_db
from ..models.auth import User
from ..core.config import settings
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from typing import Annotated
from ..core.logging import logger
from ..services.auth_service import AuthService


security = HTTPBearer()

SessionDep = Annotated[AsyncSession, Depends(get_db)]


def get_auth_service(session: SessionDep) -> AuthService:
    return AuthService(session)


AuthServiceDep = Annotated[AuthService, Depends(get_auth_service)]


async def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(security),
    db: AsyncSession = SessionDep,
):
    try:

        payload = jwt.decode(
            credentials.credentials,
            settings.SECRET_KEY,
            algorithms=[settings.ALGORITHM],
        )
        username: str = payload.get("sub")
        if username is None:
            logger.info("Invalid token")
            raise HTTPException(status_code=401, detail="Invalid token")

    except jwt.PyJWTError:
        logger.info("Invalid token")
        raise HTTPException(status_code=401, detail="Invalid token")

    user = db.query(User).filter(User.username == username).first()

    if user is None:
        logger.info("User not found")
        raise HTTPException(status_code=401, detail="User not found")

    return user
