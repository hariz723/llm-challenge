from fastapi import APIRouter, Depends
from ..schemas.auth import UserCreate, UserResponse
from ..core.dependencies import AuthServiceDep


router = APIRouter()


@router.post("/register", response_model=UserResponse)
async def register(user: UserCreate, auth_service: AuthServiceDep):
    """
    Registers a new user, given a `UserCreate` object.
    Creates a new user in the database and returns
    a JSON response containing the user's ID and an access token.
    """
    db_user = await auth_service.register_new_user(user)

    return UserResponse(
        id=db_user.id,
        username=db_user.username,
        email=db_user.email,
        access_token=await auth_service.create_user_access_token(
            user_id=db_user.id, username=db_user.username
        ),
    )
