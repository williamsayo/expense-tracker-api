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
from result import result_fail, is_fail, Either, result_ok, result_combine
from src.shared.application.services.base import BaseService
from src.identity.utils.setup_dependencies import UserDeps
from src.identity.infrastructure.adapters.dto.user import UserWriteModel, UserUpdateModel
from src.identity.domain.entities.user_entity import UserEntity
from src.identity.domain.value_objects.email_value_object import EmailValueObject
from src.identity.infrastructure.services.encryption.argon2_encrption import (
    ArgonEncryptionService,
)
from src.identity.infrastructure.mappers.user_mapper import create_unique_entity_id
from src.shared.domain.types.user_id import UserId


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
            }
        )

        result = await self.deps.repo.add(entity_result.value)
        
        if is_fail(result):
            return result_fail(result.value)

        return entity_result

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

    async def retrieve_user_usecase(self, aggregate_id: UserId) -> Either[
        UserEntity,
        IllegalArgumentError
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

        return result_ok(entity_result.value)

    async def update_user_usecase(
        self, aggregate_id: UserId, user: UserUpdateModel
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

        entity = entity_result.value
        username_or_email_exists = (
            user.username
            and await self.deps.repo.username_exists(
                user.username, entity.id, email=entity.email.value
            )
        )

        if username_or_email_exists:
            return result_fail(ConflictError(None, "Username is already taken"))

        entity.update_user(user.first_name, user.last_name, user.username)

        entity_result = await self.deps.repo.add(entity)

        if is_fail(entity_result):
            return result_fail(entity_result.value)
        
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
