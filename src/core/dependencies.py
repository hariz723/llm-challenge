from fastapi import Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select # Import select for async queries
import jwt
from typing import Annotated

# Application-specific imports
from ..models.database import get_db # Ensure get_db is imported early
from ..models.auth import User # SQLAlchemy User model
from ..schemas.auth import UserResponse # Pydantic User response model
from ..core.config import settings
from ..core.logging import logger
from ..services.auth_service import AuthService
from ..services.document_service import DocumentService
from ..repository.document import DocumentRepository
from ..storage.azure_storage import AzureStorage

from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials


security = HTTPBearer()

# Define SessionDep after all necessary imports
SessionDep = Annotated[AsyncSession, Depends(get_db)]


async def get_auth_service(session: SessionDep) -> AuthService:
    return AuthService(session)


AuthServiceDep = Annotated[AuthService, Depends(get_auth_service)]


async def get_document_repository(session: SessionDep) -> DocumentRepository:
    return DocumentRepository(session)


DocumentRepositoryDep = Annotated[DocumentRepository, Depends(get_document_repository)]


async def get_azure_storage() -> AzureStorage:
    return AzureStorage()


AzureStorageDep = Annotated[AzureStorage, Depends(get_azure_storage)]


async def get_document_service(
    document_repository: DocumentRepositoryDep,
    azure_storage: AzureStorageDep,
) -> DocumentService:
    return DocumentService(document_repository, azure_storage)


DocumentServiceDep = Annotated[DocumentService, Depends(get_document_service)]


async def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(security),
    db: AsyncSession = SessionDep,
) -> UserResponse: # Change return type to Pydantic UserResponse
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

    user = await db.execute(select(User).filter(User.username == username))
    user = user.scalar_one_or_none()

    if user is None:
        logger.info("User not found")
        raise HTTPException(status_code=401, detail="User not found")

    return UserResponse.model_validate(user) # Convert SQLAlchemy User to Pydantic UserResponse
