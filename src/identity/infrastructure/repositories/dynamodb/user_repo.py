import logging
import asyncio
from typing import Literal, Sequence
from aiodynamo.expressions import F
from aiodynamo.client import Client
from aiodynamo.errors import (
    ItemNotFound,
    ResourceInUse,
    TableAlreadyExists,
    TransactionCanceled,
)
from aiodynamo.models import KeySchema, KeySpec, KeyType, Throughput
from aiodynamo.operations import Put
from result import result_fail, result_ok, is_fail, Either
from boilerplate import (
    RepositoryNotFoundError,
    DataIntegrityError,
    RepositoryUnexpectedError,
    ConcurrencyError,
    ConflictError,
    UniqueEntityId,
    AsyncWriteRepository,
    AuthorizationError,
    ApplicationErrorID,
    GetAllOptions,
    GetOptions,
)
from src.identity.domain.entities.user_entity import UserEntity
from src.identity.infrastructure.mappers.user_mapper import UserMapper
from src.identity.infrastructure.adapters.ports.encryption import EncryptionService
from src.shared.utils.dynamo_util import build_update_expression
from src.shared.utils.type_cast import typed
from src.core.config import settings

class UserRepository(AsyncWriteRepository[UserEntity, UniqueEntityId]):
    """Repository implementation for user data."""

    USER_TABLE_NAME = settings.USER_TABLE_NAME

    def __init__(self, client: Client):
        self.client = client
        self.table = self.get_table(self.USER_TABLE_NAME)

    async def add(
        self, aggregate: UserEntity
    ) -> Either[None, RepositoryUnexpectedError | ConflictError | ConcurrencyError]:
        try:
            persistence = UserMapper.to_persistence(aggregate)
            exists = await self.exists(aggregate.id)

            if is_fail(exists):
                return result_fail(exists.value)

            if exists.value:
                await self.table.update_item(
                    {"pk": f"USER#{aggregate.id.to_string()}"},
                    update_expression=build_update_expression(persistence),
                )
            else:
                await self.client.transact_write_items(
                    [
                        Put(
                            self.USER_TABLE_NAME,
                            persistence,
                            F("pk").does_not_exist(),
                        ),
                        Put(
                            self.USER_TABLE_NAME,
                            {
                                "pk": f"EMAIL#{persistence['email']}",
                                "id": persistence["id"],
                            },
                            F("pk").does_not_exist(),
                        ),
                        Put(
                            self.USER_TABLE_NAME,
                            {
                                "pk": f"USERNAME#{persistence['username']}",
                                "id": persistence["id"],
                            },
                            F("pk").does_not_exist(),
                        ),
                    ]
                )

            return result_ok()
        except TransactionCanceled as error:
            return result_fail(ConflictError(error, "Username or email already exists"))
        except Exception as error:
            return result_fail(
                RepositoryUnexpectedError(error, "Unexpected error while adding user")
            )

    async def get_by_id(self, aggregate_id: UniqueEntityId) -> Either[
        UserEntity,
        RepositoryNotFoundError | DataIntegrityError | RepositoryUnexpectedError,
    ]:
        result = await self.table.get_item(
            {
                "pk": f"USER#{aggregate_id.to_string()}",
            },
            projection=F(
                "id",
                "email",
                "username",
                "first_name",
                "last_name",
                "version",
                "created_at",
            ),
        )

        persistence_output = result.get("Item")

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

        prefix: Literal["EMAIL", "USERNAME"] = (
            "EMAIL" if "@" in username else "USERNAME"
        )

        result = await self.table.get_item(
            {
                "pk": f"{prefix}#{username}",
            },
            projection=F("id"),
        )

        if result is None:
            return result_fail(
                RepositoryNotFoundError(Exception("User not found"), "User not found")
            )

        user_id = result["id"]

        user_result = await self.table.get_item(
            {
                "pk": f"USER#{user_id}",
            }
        )

        persistence_output = user_result["Item"]

        if not encryption.verify(password, persistence_output["password_hash"]):
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
        self, username: str, *, email: str
    ) -> Either[bool, RepositoryUnexpectedError]:
        try:
            await asyncio.gather(
                self.table.get_item({"pk": f"EMAIL#{email}"}, projection=F("pk")),
                self.table.get_item(
                    {"pk": f"USERNAME#{username}"},
                    projection=F("pk"),
                ),
            )

            return result_ok(True)
        except ItemNotFound:
            return result_ok(False)
        except Exception as error:
            return result_fail(
                RepositoryUnexpectedError(
                    error, "Unexpected error while checking username existence"
                )
            )

    async def exists(
        self, aggregate_id: UniqueEntityId
    ) -> Either[bool, RepositoryUnexpectedError]:
        try:
            await self.table.get_item(
                {
                    "pk": f"USER#{aggregate_id.to_string()}",
                },
                projection=F("pk"),
            )
            return result_ok(True)
        except ItemNotFound:
            return result_ok(False)
        except Exception as error:
            return result_fail(
                RepositoryUnexpectedError(
                    error, "Unexpected error while checking user existence"
                )
            )

    async def list(self, options: GetAllOptions) -> Sequence:
        raise NotImplementedError

    async def remove(
        self, aggregate: UserEntity
    ) -> Either[None, RepositoryUnexpectedError | ConcurrencyError | ConflictError]:
        raise NotImplementedError

    @staticmethod
    async def create_table(table_name: str, client: Client):
        try:
            table = await client.create_table(
                table_name,
                Throughput(read=5, write=5),
                KeySchema(
                    hash_key=KeySpec("pk", KeyType.string),
                ),
                wait_for_active=True,
            )
            logging.info(f"Table {table} created successfully.")
        except (TableAlreadyExists, ResourceInUse) as error:
            logging.info(f"Table {table_name} already exists.")
        except Exception as error:
            logging.error(f"Unexpected error creating table {table_name}: {error}")

    def get_table(self, table_name: str):
        return self.client.table(table_name)
