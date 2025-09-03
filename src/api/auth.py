from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from ..schemas.auth import UserCreate, UserResponse
from ..models.database import get_db
from ..services.auth_service import AuthService  # type: ignore


auth_service = AuthService()

router = APIRouter()


@router.post("/register", response_model=UserResponse)
async def register(user: UserCreate, db: AsyncSession = Depends(get_db)):
    """
    Registers a new user, given a `UserCreate` object.
    Creates a new user in the database and returns
    a JSON response containing the user's ID and an access token.
    """

    db_user = await auth_service.register_new_user(db, user)

    return UserResponse(
        id=db_user.id,
        username=db_user.username,
        email=db_user.email,
        access_token=await auth_service.create_user_access_token(
            user_id=db_user.id, username=db_user.username
        ),
    )
