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
    AsyncWriteRepository,
    AsyncReadRepository,
    AuthorizationError,
    ApplicationErrorID,
    GetAllOptions,
    GetOptions,
)
from src.identity.domain.entities.user_entity import UserEntity
from src.identity.infrastructure.repositories.schema import User
from src.identity.infrastructure.mappers.user_mapper import UserMapper
from src.identity.infrastructure.adapters.ports.encryption import EncryptionService


class UserRepository(AsyncWriteRepository[UserEntity, UniqueEntityId]):
    """Repository implementation for user data."""

    def __init__(self, db: AsyncSession):
        self.db = db

    async def add(
        self, aggregate: UserEntity, *, auto_commit: bool = True
    ) -> Either[None, RepositoryUnexpectedError | ConflictError | ConcurrencyError]:

        persistence = UserMapper.to_persistence(aggregate)
        exists = await self.exists(aggregate.id)

        if exists:
            await self.db.merge(persistence)
        else:
            self.db.add(persistence)

        if not auto_commit:
            return result_ok()

        result = await self.commit()

        if is_fail(result):
            return result_fail(result.value)

        return result

    async def get_by_id(self, aggregate_id: UniqueEntityId) -> Either[
        UserEntity,
        RepositoryNotFoundError | DataIntegrityError | RepositoryUnexpectedError,
    ]:
        query = select(User).where(User.id == aggregate_id.value)
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

        username = None

        if filter := options.get("filter"):
            username = filter.get("username", None)

        if username is None:
            return result_fail(
                RepositoryNotFoundError(
                    Exception("Username or email not provided"),
                    "Username or email not provided",
                )
            )

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
        self, username: str, aggregate_id: UniqueEntityId, *, email: str
    ) -> bool:
        query = await self.db.scalars(
            select(
                exists().where(
                    or_(User.username == username, User.email == email),
                    User.id != aggregate_id.value,
                )
            )
        )

        return cast(bool, query.one_or_none())

    async def exists(self, aggregate_id: UniqueEntityId) -> bool:
        query = await self.db.scalars(
            select(exists().where(User.id == aggregate_id.value))
        )
        return cast(bool, query.one_or_none())

    async def list(self, options: GetAllOptions) -> Sequence:
        raise NotImplementedError

    async def remove(
        self, aggregate: UserEntity
    ) -> Either[None, RepositoryUnexpectedError | ConcurrencyError | ConflictError]:
        raise NotImplementedError

    async def commit(
        self,
    ) -> Either[None, RepositoryUnexpectedError | ConflictError]:
        try:
            await self.db.commit()
            return result_ok()
        except IntegrityError as error:
            await self.db.rollback()
            return result_fail(ConflictError(error, "Username or email already exists"))
        except Exception as error:
            await self.db.rollback()
            return result_fail(RepositoryUnexpectedError(error))
