from fastapi import APIRouter
from ..schemas.auth import (
    UserCreate,
    UserRegisterResponse,
    UserLogin,
    UserLoginResponse,
    CurrentUserResponse,
)
from ..core.dependencies import AuthServiceDep, CurrentUserdep
import core.constants as cons

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
        token_type=cons.TOKEN_TYPE,
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
        access_token=access_token, token_type=cons.TOKEN_TYPE, user_id=db_user.id
    )


@router.get("/me", response_model=CurrentUserResponse)
async def get_current_user_info(
    auth_service: AuthServiceDep, current_user=CurrentUserdep
):
    """
    Retrieves information about the currently authenticated user.
    Returns a JSON response containing the user's ID, username, email, and an access token.
    """

    access_token = await auth_service.create_user_access_token(
        user_id=current_user.id, username=current_user.username
    )
    return CurrentUserResponse(
        id=current_user.id,
        username=current_user.username,
        email=current_user.email,
        access_token=access_token,
        token_type=cons.TOKEN_TYPE,
    )
