from fastapi import APIRouter
from ..schemas.auth import (
    UserCreate,
    UserRegisterResponse,
    UserLogin,
    UserLoginResponse,
)
from ..core.dependencies import AuthServiceDep


router = APIRouter()


@router.post("/register", response_model=UserRegisterResponse)
async def register(user: UserCreate, auth_service: AuthServiceDep):
    """
    Registers a new user, given a `UserCreate` object.
    Creates a new user in the database and returns
    a JSON response containing the user's ID and an access token.
    """

    db_user = await auth_service.register_new_user(user)

    return UserRegisterResponse(
        id=db_user.id,
        username=db_user.username,
        email=db_user.email,
        access_token=await auth_service.create_user_access_token(
            user_id=db_user.id, username=db_user.username
        ),
        token_type="bearer",
    )


@router.post("/login", response_model=UserLoginResponse)
async def login(user: UserLogin, auth_service: AuthServiceDep):
    """
    Logs in a user, given a `UserLogin` object.
    Authenticates the user credentials against the database,
    and returns a JSON response containing an access token
    if the credentials are valid.
    """

    db_user = await auth_service.authenticate_user(
        username=user.username, password=user.password
    )

    access_token = await auth_service.create_user_access_token(
        user_id=db_user.id, username=db_user.username
    )
    return UserLoginResponse(
        access_token=access_token,
        token_type="bearer",
        user_id=db_user.id
    )
