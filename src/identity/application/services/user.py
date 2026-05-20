from uuid import UUID
from boilerplate import (
    RepositoryUnexpectedError,
    ConflictError,
    ConcurrencyError,
    DataIntegrityError,
    RepositoryNotFoundError,
    IllegalArgumentError,
    DomainRuleError,
    UnexpectedError,
    CoreError,
    AuthorizationError,
)
from fastapi import UploadFile
from result import result_fail, is_fail, Either, result_ok, result_combine
from src.identity.utils.validators import FileValidator
from src.shared.application.services.base import BaseService
from src.identity.utils.setup_dependencies import UserDeps
from src.identity.infrastructure.adapters.dto.user import (
    ResetPasswordModel,
    UserWriteModel,
    UserUpdateModel,
)
from src.identity.domain.entities.user_entity import UserEntity
from src.identity.domain.value_objects.email_value_object import EmailValueObject
from src.identity.infrastructure.services.encryption.argon2_encrption import (
    ArgonEncryptionService,
)
from src.identity.infrastructure.mappers.user_mapper import create_unique_entity_id


class UserService(BaseService[UserDeps]):
    """Service layer."""

    def __init__(
        self,
        deps: UserDeps,
    ):
        super().__init__(deps)

    async def create_user_usecase(self, user: UserWriteModel) -> Either[
        UserEntity,
        DomainRuleError | RepositoryUnexpectedError | ConflictError | ConcurrencyError,
    ]:
        email_result = EmailValueObject.create({"value": user.email})
        encryption = ArgonEncryptionService()
        hashed_password = encryption.hash(user.password)

        if is_fail(email_result):
            return result_fail(email_result.value)

        entity_result = UserEntity.create(
            {
                "email": email_result.value,
                "first_name": user.first_name,
                "last_name": user.last_name,
                "username": user.username,
                "hashed_password": hashed_password,
                "avatar": None,
            }
        )

        result = await self.deps.repo.add(entity_result.value)

        if is_fail(result):
            return result_fail(result.value)

        return entity_result

    async def delete_user_usecase(self, aggregate_id: UUID) -> Either[
        None,
        RepositoryNotFoundError | RepositoryUnexpectedError | DataIntegrityError,
    ]:
        entity_id_result = create_unique_entity_id(aggregate_id)

        if is_fail(entity_id_result):
            return result_fail(
                RepositoryNotFoundError(entity_id_result.value, "User not found")
            )

        result = await self.deps.repo.get_by_id(entity_id_result.value)

        if is_fail(result):
            return result_fail(result.value)

        user_entity = result.value

        user_entity.discard()

        await self.deps.repo.add(user_entity)

        return result_ok()

    async def authenticate_user_usecase(self, username: str, password: str) -> Either[
        dict[str, str],
        DataIntegrityError
        | RepositoryNotFoundError
        | RepositoryUnexpectedError
        | UnexpectedError
        | AuthorizationError,
    ]:
        encryption = self.deps.argon2_encryption_service
        entity_result = await self.deps.repo.first(
            {"filter": {"username": username}},
            encryption,
            password,
        )

        if is_fail(entity_result):
            return entity_result

        user_entity = entity_result.value

        if encryption.password_needs_rehash(user_entity.hashed_password):
            new_hash = encryption.hash(password)
            user_entity.set_new_hash(new_hash)
            await self.deps.repo.add(user_entity)

        result = self.issue_jwt_tokens(user_entity.id.value)

        if is_fail(result):
            return result_fail(
                UnexpectedError(result.value, "Unable to generate authentication token")
            )

        return result

    async def retrieve_user_usecase(self, aggregate_id: UUID) -> Either[
        UserEntity,
        CoreError
        | IllegalArgumentError
        | DataIntegrityError
        | RepositoryNotFoundError
        | RepositoryUnexpectedError,
    ]:
        entity_id_result = create_unique_entity_id(aggregate_id)

        if is_fail(entity_id_result):
            return result_fail(
                IllegalArgumentError(entity_id_result.value, "Invalid user ID")
            )

        entity_result = await self.deps.repo.get_by_id(entity_id_result.value)

        if is_fail(entity_result):
            return result_fail(entity_result.value)

        entity = entity_result.value

        if entity.avatar:
            cloudfront_result = self.deps.cdn_service.signed_url(entity.avatar)

            if is_fail(cloudfront_result):
                return result_fail(cloudfront_result.value)

            entity.update_avatar(cloudfront_result.value)

        return result_ok(entity_result.value)

    async def update_user_usecase(
        self,
        aggregate_id: UUID,
        user: UserUpdateModel,
        avatar: UploadFile | None = None,
    ) -> Either[
        UserEntity,
        CoreError
        | DataIntegrityError
        | RepositoryNotFoundError
        | RepositoryUnexpectedError,
    ]:
        entity_id_result = create_unique_entity_id(aggregate_id)

        if is_fail(entity_id_result):
            return result_fail(
                RepositoryNotFoundError(entity_id_result.value, "User not found")
            )

        entity_result = await self.deps.repo.get_by_id(entity_id_result.value)

        if is_fail(entity_result):
            return result_fail(entity_result.value)

        avatar_url = None

        if avatar is not None:
            result = await FileValidator().handle_file_validation(avatar)

            if is_fail(result):
                return result_fail(result.value)

            avatar_url = await self.deps.object_storage.upload_avatar(
                result.value, avatar.file
            )

            if is_fail(avatar_url):
                return result_fail(avatar_url.value)

            avatar_url = avatar_url.value

        entity = entity_result.value

        username_or_email_exists = (
            user.username
            and await self.deps.repo.username_exists(
                user.username, entity.id, email=entity.email.value
            )
        )

        if username_or_email_exists:
            return result_fail(ConflictError(None, "Username is already taken"))

        entity.update_user(
            user.first_name, user.last_name, user.username, avatar=avatar_url
        )

        entity_result = await self.deps.repo.add(entity)

        if is_fail(entity_result):
            return result_fail(entity_result.value)

        if entity.avatar:
            cloudfront_result = self.deps.cdn_service.signed_url(entity.avatar)

            if is_fail(cloudfront_result):
                return cloudfront_result
            
            entity.update_avatar(cloudfront_result.value)

        return result_ok(entity)

    def issue_jwt_tokens(
        self, aggregate_id: str | UUID
    ) -> Either[dict[str, str], UnexpectedError]:
        id = str(aggregate_id)
        access_token_result = self.deps.token_service.create_access_token(id)
        refresh_token_result = self.deps.token_service.create_refresh_token(id)

        result = result_combine((access_token_result, refresh_token_result))

        if is_fail(result):
            return result

        access_token, refresh_token = result.value

        return result_ok({"access_token": access_token, "refresh_token": refresh_token})

    async def refresh_access_token_usecase(
        self, refresh_token: str
    ) -> Either[dict[str, str], UnexpectedError | AuthorizationError]:
        access_token = self.deps.token_service.verify_refresh_token(refresh_token)

        if is_fail(access_token):
            return access_token

        return result_ok({"access_token": access_token.value})

    async def reset_user_password_usecase(
        self, user_id: UUID, reset_password_data: ResetPasswordModel
    ) -> Either[None, CoreError | AuthorizationError]:

        entity_id_result = create_unique_entity_id(user_id)
        if is_fail(entity_id_result):
            return result_fail(
                IllegalArgumentError(entity_id_result.value, "Invalid user ID")
            )

        entity_result = await self.deps.repo.get_by_id(entity_id_result.value)

        if is_fail(entity_result):
            return result_fail(entity_result.value)

        entity = entity_result.value

        if not self.deps.argon2_encryption_service.verify(
            reset_password_data.old_password, entity.hashed_password
        ):
            return result_fail(AuthorizationError("Current password is incorrect"))

        if reset_password_data.password != reset_password_data.confirm_password:
            return result_fail(IllegalArgumentError(None, "Passwords do not match"))

        new_hashed_password = self.deps.argon2_encryption_service.hash(
            reset_password_data.password
        )

        entity.change_password(new_hashed_password)

        entity_result = await self.deps.repo.add(entity)

        if is_fail(entity_result):
            return result_fail(entity_result.value)

        return result_ok()

    async def upload_user_avatar_usecase(
        self, user_id: UUID, avatar: UploadFile
    ) -> Either[str, CoreError | RepositoryNotFoundError | RepositoryUnexpectedError]:

        filename_result = await FileValidator().handle_file_validation(avatar)

        if is_fail(filename_result):
            return result_fail(filename_result.value)

        filename = filename_result.value

        entity_id_result = create_unique_entity_id(user_id)

        if is_fail(entity_id_result):
            return result_fail(
                IllegalArgumentError(entity_id_result.value, "Invalid user ID")
            )

        entity_result = await self.deps.repo.get_by_id(entity_id_result.value)

        if is_fail(entity_result):
            return result_fail(entity_result.value)

        entity = entity_result.value

        upload_result = await self.deps.object_storage.upload_avatar(
            filename, avatar.file
        )

        if is_fail(upload_result):
            return result_fail(upload_result.value)

        avatar_url = upload_result.value

        entity.update_avatar(avatar_url)

        entity_result = await self.deps.repo.add(entity)

        if is_fail(entity_result):
            return result_fail(entity_result.value)

        return result_ok(avatar_url)
