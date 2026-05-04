from typing import Sequence, cast
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, exists, or_
from sqlalchemy.exc import IntegrityError
from result import result_fail, result_ok, is_fail, Either
from boilerplate import (
    RepositoryNotFoundError,
    DataIntegrityError,
    RepositoryUnexpectedError,
    ConcurrencyError,
    ConflictError,
    UniqueEntityId,
    WriteRepository,
    ReadRepository,
    AuthorizationError,
    ApplicationErrorID,
    GetAllOptions,
    GetOptions,
)
from identity.domain.entities.user_entity import UserEntity
from identity.infrastructure.repositories.schema import User
from identity.infrastructure.mappers.user_mapper import UserMapper
from identity.infrastructure.adapters.ports.encryption import EncryptionService


class UserRepository(WriteRepository, ReadRepository):
    """Repository implementation for user data."""

    def __init__(self, db: AsyncSession):
        self.db = db

    async def add(
        self, aggregate: UserEntity
    ) -> Either[
        UserEntity, RepositoryUnexpectedError | ConflictError | ConcurrencyError
    ]:
        try:
            persistence = UserMapper.to_persistence(aggregate)
            exists = await self.exists(aggregate.id)

            if exists:
                await self.db.merge(persistence)
            else:
                self.db.add(persistence)

            await self.db.commit()
            return result_ok(aggregate)
        except IntegrityError as error:
            await self.db.rollback()
            return result_fail(ConflictError(error, "Username or email already exists"))
        except Exception as error:
            await self.db.rollback()
            return result_fail(RepositoryUnexpectedError(error))

    async def get_by_id(self, aggregateId: UniqueEntityId) -> Either[
        UserEntity,
        RepositoryNotFoundError | DataIntegrityError | RepositoryUnexpectedError,
    ]:
        query = select(User).where(User.id == aggregateId.value)
        persistence_output = (await self.db.scalars(query)).one_or_none()

        if not persistence_output:
            return result_fail(
                RepositoryNotFoundError(Exception("User not found"), "User not found")
            )

        result = UserMapper.to_domain(persistence_output)

        if is_fail(result):
            return result_fail(DataIntegrityError(Exception(result.value)))

        return result_ok(result.value)

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

        result = await self.db.scalars(
            select(User).where(or_(User.username == username, User.email == username))
        )
        persistence_output = result.one_or_none()

        if not persistence_output:
            return result_fail(
                RepositoryNotFoundError(Exception("User not found"), "User not found")
            )

        if not encryption.verify(password, persistence_output.password_hash):
            return result_fail(
                AuthorizationError(
                    ApplicationErrorID.AUTHORIZATION,
                    "Incorrect username or password",
                )
            )

        result = UserMapper.to_domain(persistence_output)
        if is_fail(result):
            return result_fail(DataIntegrityError(Exception(result.value)))

        return result_ok(result.value)

    async def username_exists(
        self, username: str, aggregateId: UniqueEntityId, *, email: str
    ) -> bool:
        query = await self.db.scalars(
            select(
                exists().where(
                    or_(User.username == username, User.email == email),
                    User.id != aggregateId.value,
                )
            )
        )

        return cast(bool, query.one_or_none())

    async def exists(self, aggregateId: UniqueEntityId) -> bool:
        query = await self.db.scalars(
            select(exists().where(User.id == aggregateId.value))
        )
        return cast(bool, query.one_or_none())

    async def list(self, options: GetAllOptions) -> Sequence:
        raise NotImplementedError

    def remove(
        self, aggregate: UserEntity
    ) -> Either[None, RepositoryUnexpectedError | ConcurrencyError | ConflictError]:
        raise NotImplementedError
