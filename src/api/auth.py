from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from src.schemas.auth import UserCreate, UserResponse
from src.models.database import get_db
from src.services import auth_service


router = APIRouter()


@router.post("/register", response_model=UserResponse)
async def register(user: UserCreate, db: AsyncSession = Depends(get_db)):
    """
    Registers a new user, given a `UserCreate` object.
    Creates a new user in the database and returns
    a JSON response containing the user's ID and an access token.
    """

    db_user = await auth_service.register_new_user(db, user)

    return UserResponse(db_user)
