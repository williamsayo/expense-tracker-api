import logging
from typing import Sequence, cast
from aiodynamo.errors import ResourceInUse, ItemNotFound
from aiodynamo.expressions import HashKey, F
from aiodynamo.client import Client
from aiodynamo.models import (
    KeySchema,
    GlobalSecondaryIndex,
    KeySpec,
    KeyType,
    Projection,
    ProjectionType,
    Throughput,
)
from boilerplate import (
    DataIntegrityError,
    RepositoryUnexpectedError,
    ConflictError,
    ConcurrencyError,
    RepositoryNotFoundError,
    GetAllOptions,
    GetOptions,
    AuthenticationError,
    AuthenticationError,
    AsyncWriteRepository,
    UniqueEntityId,
)
from result import result_fail, result_ok, is_fail, Either, result_combine
from src.shared.utils.dynamo_util import build_condition, build_update_expression
from src.spending.expenses.domain.entities.expense_entity import ExpenseEntity
from src.spending.expenses.infrastructure.mappers.expense import ExpenseMapper


from src.spending.expenses.infrastructure.repositories.schema import ExpenseSchema


class ExpenseRepository(AsyncWriteRepository[ExpenseEntity, UniqueEntityId]):
    """Repository implementation for expense data."""

    TABLE_NAME = "expense"

    def __init__(self, client: Client):
        self.client = client
        self.table = self.expense_table(self.TABLE_NAME, client)

    async def list(
        self, options: GetAllOptions[str]
    ) -> Either[
        Sequence[ExpenseEntity], RepositoryUnexpectedError | DataIntegrityError
    ]:
        filter = options.get("filter")

        if filter is None:
            return result_fail(
                RepositoryUnexpectedError(Exception("filter options is required"))
            )

        auth_id = options.get("auth_id")

        if auth_id is None:
            return result_fail(
                RepositoryUnexpectedError(
                    Exception("auth_id is required in filter options")
                )
            )

        query = await self.table.query_single_page(
            key_condition=HashKey("auth_id", auth_id),
            limit=options.get("limit"),
        )

        persistence_output = query.items

        result = tuple(
            ExpenseMapper.to_domain(persistence) for persistence in persistence_output
        )
        entity_result = result_combine(result)

        if is_fail(entity_result):
            return result_fail(DataIntegrityError(Exception(entity_result.value)))

        return result_ok(entity_result.value)

    async def get_by_id(self, aggregate_id: UniqueEntityId) -> Either[
        ExpenseEntity,
        RepositoryNotFoundError | DataIntegrityError | RepositoryUnexpectedError,
    ]:
        result = await self.table.get_item({"id": aggregate_id.to_string()})

        if result is None:
            return result_fail(
                RepositoryNotFoundError(
                    Exception("Expense not found"), "Expense not found"
                )
            )

        entity_result = ExpenseMapper.to_domain(result)

        if is_fail(entity_result):
            return result_fail(DataIntegrityError(Exception(entity_result.value)))

        return result_ok(entity_result.value)

    async def add(
        self, aggregate: ExpenseEntity
    ) -> Either[None, RepositoryUnexpectedError | ConflictError | ConcurrencyError]:
        try:
            persistence = ExpenseMapper.to_persistence(aggregate)

            exists = await self.exists(aggregate.id)

            if is_fail(exists):
                return result_fail(exists.value)

            if exists:
                condition = F("version").equals(aggregate.version)
                await self.table.update_item(
                    {"id": persistence["id"]},
                    update_expression=build_update_expression(persistence),
                    condition=condition,
                )
            else:
                await self.table.put_item(persistence)

            return result_ok()
        except Exception as error:
            return result_fail(RepositoryUnexpectedError(error))

    async def exists(
        self, aggregate_id: UniqueEntityId
    ) -> Either[bool, RepositoryUnexpectedError]:
        try:
            response = await self.table.get_item(
                {
                    "id": aggregate_id.to_string(),
                }
            )
            return result_ok(True)
        except ItemNotFound:
            return result_ok(False)
        except Exception:
            return result_fail(RepositoryUnexpectedError())

    async def first(self, options: GetOptions) -> Either[
        ExpenseEntity,
        RepositoryNotFoundError | DataIntegrityError | RepositoryUnexpectedError,
    ]:
        filter = options.get("filter")

        if filter is None:
            return result_fail(
                RepositoryUnexpectedError(Exception("filter options is required"))
            )

        auth_id = filter.get("auth_id")

        if auth_id is None:
            return result_fail(
                RepositoryUnexpectedError(
                    Exception("auth_id is required in filter options")
                )
            )

        response = await self.table.query_single_page(
            HashKey("auth_id", auth_id),
            index="auth_id",
            filter_expression=build_condition(filter),
            limit=1,
        )

        result = response.items[0]

        if result is None:
            return result_fail(
                RepositoryNotFoundError(
                    Exception("Expense not found"), "Expense not found"
                )
            )

        result = ExpenseMapper.to_domain(result)

        if is_fail(result):
            return result_fail(DataIntegrityError(Exception(result.value)))

        return result_ok(result.value)

    async def remove(
        self, aggregate: ExpenseEntity
    ) -> Either[None, RepositoryUnexpectedError]:

        try:
            await self.table.delete_item(
                {"id": aggregate.id.to_string()},
                condition=F("auth_id").exists(),
            )
        except Exception as error:
            return result_fail(RepositoryUnexpectedError(error))

        return result_ok()

    @staticmethod
    async def create_table(table_name: str, client: Client):
        try:
            table = await client.create_table(
                table_name,
                Throughput(read=5, write=5),
                KeySchema(
                    hash_key=KeySpec("id", KeyType.string),
                    range_key=KeySpec("date", KeyType.string),
                ),
                wait_for_active=True,
                gsis=[
                    GlobalSecondaryIndex(
                        "auth_id-date-index",
                        KeySchema(
                            hash_key=KeySpec("auth_id", KeyType.string),
                            range_key=KeySpec("date", KeyType.string),
                        ),
                        Projection(ProjectionType.all),
                        Throughput(read=2, write=2),
                    ),
                    GlobalSecondaryIndex(
                        "auth_id-category-index",
                        KeySchema(
                            hash_key=KeySpec("auth_id", KeyType.string),
                            range_key=KeySpec("category", KeyType.string),
                        ),
                        Projection(ProjectionType.all),
                        Throughput(read=2, write=2),
                    ),
                    GlobalSecondaryIndex(
                        "auth_id-amount-index",
                        KeySchema(
                            hash_key=KeySpec("auth_id", KeyType.string),
                            range_key=KeySpec("amount", KeyType.number),
                        ),
                        Projection(ProjectionType.all),
                        Throughput(read=2, write=2),
                    ),
                    GlobalSecondaryIndex(
                        "budget_id-date-index",
                        KeySchema(
                            hash_key=KeySpec("budget_id", KeyType.string),
                            range_key=KeySpec("date", KeyType.string),
                        ),
                        Projection(ProjectionType.all),
                        Throughput(read=2, write=2),
                    ),
                ],
            )
            logging.info(f"Table {table} created successfully.")
        except ResourceInUse as error:
            logging.info(f"Table {table_name} already exists.")
        except Exception as error:
            logging.error(f"Unexpected error creating table {table_name}: {error}")

    def expense_table(self, table_name: str, client: Client):
        return client.table(table_name)
