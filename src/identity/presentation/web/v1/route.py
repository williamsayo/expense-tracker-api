from fastapi.routing import APIRouter
from fastapi.security import OAuth2PasswordRequestForm
from fastapi import Depends, status
from typing import Annotated
from result import is_fail
from src.identity.infrastructure.adapters.dto.token import (
    RefreshTokenData,
    TokenData,
    AccessTokenData,
)
from src.identity.application.services.user import UserService
from src.identity.infrastructure.adapters.dto.user import (
    ResetPasswordModel,
    UserAvatarReadModel,
    UserWriteModel,
    UserLoginModel,
    UserUpdateModel,
    UserReadModel,
)
from src.shared.application.dtos.upload import FileUploadDTO
from src.shared.utils.auth.dependencies import AuthDeps
from src.shared.utils.setup_dependencies import (
    validate_image_upload,
    validate_optional_image_upload,
)

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
    "/refresh-token", response_model=AccessTokenData, status_code=status.HTTP_200_OK
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


@router.post(
    "/reset-password",
    status_code=status.HTTP_200_OK,
    description="Endpoint to reset a user's password.",
    response_description="A message indicating the password reset was successful.",
    summary="Reset User Password",
    responses={
        200: {"description": "Password reset successfully"},
        400: {"description": "Invalid input data or token"},
        401: {"description": "Unauthorized - invalid or expired token"},
        500: {"description": "Internal server error"},
    },
)
async def reset_user_password(
    auth: AuthDeps,
    reset_password_data: ResetPasswordModel,
    user_service: Annotated[UserService, Depends()],
):
    """Endpoint to reset a user's password."""
    token_result = await user_service.reset_user_password_usecase(
        auth.user_id, reset_password_data
    )

    if is_fail(token_result):
        raise token_result.value

    return {"message": "Password reset successfully"}


@router.post("/register", status_code=status.HTTP_201_CREATED)
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


@router.patch(
    "/profile", response_model=UserReadModel, status_code=status.HTTP_200_OK
)
async def update_user_details(
    user_data: Annotated[UserUpdateModel, Depends(UserUpdateModel.form)],
    auth: AuthDeps,
    user_service: Annotated[UserService, Depends()],
    avatar: Annotated[
        FileUploadDTO | None,
        Depends(validate_optional_image_upload),
    ],
):
    user_result = await user_service.update_user_usecase(
        auth.user_id, user_data, avatar
    )

    if is_fail(user_result):
        raise user_result.value

    return user_result.value


@router.patch(
    "/avatar",
    response_model=UserAvatarReadModel,
    status_code=status.HTTP_200_OK,
    summary="Upload or update user avatar",
    description="Endpoint to upload or update a user's avatar image.",
    response_description="The URL of the uploaded avatar image.",
    responses={
        200: {"description": "Avatar uploaded successfully"},
        400: {"description": "Invalid image file or upload error"},
        401: {"description": "Unauthorized - invalid or expired token"},
        413: {"description": "Uploaded file is too large"},
        415: {"description": "Unsupported media type - invalid image format"},
        500: {"description": "Internal server error"},
    },
    name="upload_avatar",
)
async def upload_profile_avatar(
    auth: AuthDeps,
    user_service: Annotated[UserService, Depends()],
    avatar: Annotated[FileUploadDTO, Depends(validate_image_upload)],
):

    user_result = await user_service.upload_user_avatar_usecase(auth.user_id, avatar)

    if is_fail(user_result):
        raise user_result.value

    return {"avatar": user_result.value}
