from fastapi.routing import APIRouter
from fastapi.security import OAuth2PasswordRequestForm
from fastapi import Depends,status
from typing import Annotated
from result import is_fail
from identity.infrastructure.adapters.dto.token import (
    RefreshTokenData,
    TokenData,
    AccessTokenData,
)
from identity.application.services.user import UserService
from identity.infrastructure.adapters.dto.user import (
    UserWriteModel,
    UserLoginModel,
    UserUpdateModel,
    UserReadModel,
)
from shared.utils.auth.dependencies import AuthDeps

router = APIRouter(
    prefix="/auth",
    tags=["Authentication"],
)


@router.post("/token", response_model=TokenData, status_code=status.HTTP_200_OK)
async def authenticate_user_for_access_token(
    form_data: Annotated[OAuth2PasswordRequestForm, Depends()],
    user_service: Annotated[UserService, Depends()],
):
    """Endpoint to authenticate a user and return a token."""
    token_result = await user_service.authenticate_user_usecase(
        form_data.username, form_data.password
    )
    if is_fail(token_result):
        raise token_result.value

    return token_result.value


@router.post(
    "/refresh-token",
    response_model=AccessTokenData,
    status_code=status.HTTP_200_OK
)
async def refresh_access_token(
    token: RefreshTokenData,
    user_service: Annotated[UserService, Depends()],
):
    """Endpoint to refresh a user's access token."""
    token_result = await user_service.refresh_access_token_usecase(token.refresh_token)

    if is_fail(token_result):
        raise token_result.value

    return token_result.value

@router.post("/register",status_code=status.HTTP_201_CREATED)
async def register_user(
    user_data: UserWriteModel, user_service: Annotated[UserService, Depends()]
):
    """Endpoint to register a new user."""
    user_result = await user_service.create_user_usecase(user_data)

    if is_fail(user_result):
        raise user_result.value

    return {"message": "User registered successfully"}


@router.post("/login", response_model=TokenData, status_code=status.HTTP_200_OK)
async def login_user(
    credentials: UserLoginModel,
    user_service: Annotated[UserService, Depends()],
):
    """Endpoint to authenticate a user and return a token."""
    token_result = await user_service.authenticate_user_usecase(
        credentials.email, credentials.password
    )
    if is_fail(token_result):
        raise token_result.value

    return token_result.value


@router.get("/profile", response_model=UserReadModel, status_code=status.HTTP_200_OK)
async def retrieve_user_details(
    auth: AuthDeps,
    user_service: Annotated[UserService, Depends()],
):
    user_result = await user_service.retrieve_user_usecase(auth.user_id)
    if is_fail(user_result):
        raise user_result.value

    return user_result.value


@router.patch("/update_profile", response_model=UserReadModel, status_code=status.HTTP_200_OK)
async def update_user_details(
    user_data: UserUpdateModel,
    auth: AuthDeps,
    user_service: Annotated[UserService, Depends()],
):
    user_result = await user_service.update_user_usecase(auth.user_id, user_data)

    if is_fail(user_result):
        raise user_result.value

    return user_result.value
