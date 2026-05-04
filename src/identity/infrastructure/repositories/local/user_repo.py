from typing import Sequence
from uuid import UUID
from result import result_fail, result_ok, Either
from boilerplate import (
    RepositoryNotFoundError,
    DataIntegrityError,
    RepositoryUnexpectedError,
    ConcurrencyError,
    ConflictError,
    UniqueEntityId,
    WriteRepository,
    ReadRepository,
    GetAllOptions,
    GetOptions,
    AuthorizationError,
    ApplicationErrorID,
)
from identity.domain.entities.user_entity import UserEntity
from identity.infrastructure.adapters.ports.encryption import EncryptionService


class LocalUserRepository(WriteRepository, ReadRepository):
    """Repository implementation for local user data."""

    db: dict[str | UUID, UserEntity] = {}

    async def add(
        self, aggregate: UserEntity
    ) -> Either[
        UserEntity, RepositoryUnexpectedError | ConflictError | ConcurrencyError
    ]:
        for keys, value in self.db.items():
            if keys != aggregate.id.value and (
                value.username == aggregate.username or value.email == aggregate.email
            ):
                return result_fail(
                    ConflictError(
                        Exception("Username or email already exists"),
                        "Username or email already exists",
                    )
                )

        self.db[aggregate.id.value] = aggregate
        return result_ok(aggregate)

    async def get_by_id(self, aggregateId: UniqueEntityId) -> Either[
        UserEntity,
        RepositoryNotFoundError | DataIntegrityError | RepositoryUnexpectedError,
    ]:
        result = self.db.get(aggregateId.value)

        if result is None:
            return result_fail(RepositoryNotFoundError(Exception("User not found")))
        return result_ok(result)

    async def first(
        self, options: GetOptions, encryption: EncryptionService, password: str
    ) -> Either[
        UserEntity,
        RepositoryNotFoundError
        | DataIntegrityError
        | RepositoryUnexpectedError
        | AuthorizationError,
    ]:
        if filter := options.get("filter"):
            username = filter.get("username", None)

        result = None

        for entity in self.db.values():
            if entity.username == username or entity.email == username:
                result = entity

        if result is None:
            return result_fail(
                RepositoryNotFoundError(Exception("User not found"), "User not found")
            )

        if not encryption.verify(password, result.hashed_password):
            return result_fail(
                AuthorizationError(
                    ApplicationErrorID.AUTHORIZATION,
                    "Incorrect username or password",
                )
            )

        return result_ok(result)

    async def username_exists(
        self, username: str, aggregateId: UniqueEntityId, *, email: str
    ) -> bool:
        for keys, value in self.db.items():
            return (
                keys != aggregateId
                and value.username == username
                and value.email == email
            )

        return False

    async def exists(self, aggregateId: UniqueEntityId) -> bool:
        query = self.db.get(aggregateId.value)
        return query is not None

    async def list(self, options: GetAllOptions) -> Sequence:
        raise NotImplementedError

    def remove(
        self, aggregate: UserEntity
    ) -> Either[None, RepositoryUnexpectedError | ConcurrencyError | ConflictError]:
        raise NotImplementedError
