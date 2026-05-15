from datetime import datetime, timezone
import logging
from typing import Sequence, cast
from aiodynamo.client import Client
from aiodynamo.errors import ItemNotFound, ResourceInUse, TableAlreadyExists
from aiodynamo.expressions import F, HashKey
from aiodynamo.errors import TableAlreadyExists
from aiodynamo.models import (
    KeySchema,
    KeySpec,
    KeyType,
    Projection,
    ProjectionType,
    Throughput,
    GlobalSecondaryIndex,
    LocalSecondaryIndex,
)
from boilerplate import (
    AsyncWriteRepository,
    ConcurrencyError,
    ConflictError,
    DataIntegrityError,
    RepositoryNotFoundError,
    RepositoryUnexpectedError,
    UniqueEntityId,
    GetAllOptions,
    GetOptions,
)

from result import Either, result_combine, result_ok, result_fail, is_fail
from src.shared.utils.dynamo_util import build_condition, build_update_expression
from src.spending.budgeting.domain.entities.budget_entity import BudgetEntity
from src.spending.budgeting.infrastructure.mappers.budget_mapper import BudgetMapper
from src.spending.budgeting.infrastructure.repositories.schema import BudgetSchema


class BudgetRepository(AsyncWriteRepository[BudgetEntity, UniqueEntityId]):
    """Repository implementation for budget data."""

    TABLE_NAME = "budget"

    def __init__(self, client: Client):
        self.client = client
        self.table = self.budget_table(self.TABLE_NAME)

    async def list(
        self, options: GetAllOptions[str]
    ) -> Either[Sequence[BudgetEntity], RepositoryUnexpectedError | DataIntegrityError]:
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

        condition = build_condition(filter)

        if "start_date" in filter or "end_date" in filter:
            condition = (
                condition
                & F("start_date").gte(filter["start_date"])
                & F("end_date").lte(filter["end_date"])
            )

        query = await self.table.query_single_page(
            key_condition=HashKey("auth_id", auth_id),
            filter_expression=condition,
            limit=options.get("limit"),
        )

        persistence_output = query.items

        result = tuple(
            BudgetMapper.to_domain(persistence) for persistence in persistence_output
        )
        
        entity_result = result_combine(result)

        if is_fail(entity_result):
            return result_fail(DataIntegrityError(Exception(entity_result.value)))

        return result_ok(entity_result.value)

    async def get_by_id(self, aggregate_id: UniqueEntityId) -> Either[
        BudgetEntity,
        RepositoryNotFoundError | DataIntegrityError | RepositoryUnexpectedError,
    ]:
        result = await self.table.get_item({"id": aggregate_id.to_string()})

        if result is None:
            return result_fail(
                RepositoryNotFoundError(
                    Exception("Budget not found"), "Budget not found"
                )
            )

        entity_result = BudgetMapper.to_domain(result)

        if is_fail(entity_result):
            return result_fail(DataIntegrityError(Exception(entity_result.value)))

        return result_ok(entity_result.value)

    async def add(
        self, aggregate: BudgetEntity
    ) -> Either[None, RepositoryUnexpectedError | ConflictError | ConcurrencyError]:
        try:
            persistence = BudgetMapper.to_persistence(aggregate)

            exists = await self.exists(aggregate.id)

            if is_fail(exists):
                return result_fail(exists.value)

            if exists.value:
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
            await self.table.get_item(
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
        BudgetEntity,
        RepositoryNotFoundError | DataIntegrityError | RepositoryUnexpectedError,
    ]:
        filter = options.get("filter")

        if filter is None:
            return result_fail(
                RepositoryUnexpectedError(Exception("filter options is required"))
            )

        result = await self.table.get_item(filter)

        if result is None:
            return result_fail(
                RepositoryNotFoundError(
                    Exception("Budget not found"), "Budget not found"
                )
            )

        entity = BudgetMapper.to_domain(result)

        if is_fail(entity):
            return result_fail(DataIntegrityError(Exception(entity.value)))

        return result_ok(entity.value)

    async def remove(
        self, aggregate: BudgetEntity
    ) -> Either[None, RepositoryUnexpectedError]:

        try:
            await self.table.update_item(
                {"id": aggregate.id.to_string(), "auth_id": str(aggregate.auth_id)},
                update_expression=F("is_deleted").set(True)
                & F("deleted_at").set(datetime.now(timezone.utc).isoformat()),
                condition=F("id").exists() & F("auth_id").exists(),
            )
        except Exception as error:
            print("Error removing expense:", error)
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
                    range_key=KeySpec("start_date", KeyType.string),
                ),
                gsis=[
                    GlobalSecondaryIndex(
                        "auth_id-start_date-index",
                        KeySchema(
                            hash_key=KeySpec("auth_id", KeyType.string),
                            range_key=KeySpec("start_date", KeyType.string),
                        ),
                        Projection(ProjectionType.all),
                        Throughput(read=2, write=2),
                    ),
                    GlobalSecondaryIndex(
                        "auth_id-currency-index",
                        KeySchema(
                            hash_key=KeySpec("auth_id", KeyType.string),
                            range_key=KeySpec("currency", KeyType.string),
                        ),
                        Projection(ProjectionType.all),
                        Throughput(read=2, write=2),
                    ),
                ],
                wait_for_active=True,
            )
            logging.info(f"Table {table} created successfully.")
        except ResourceInUse as e:
            logging.info(f"Table {table_name} already exists.")
        except Exception as e:
            logging.error(f"Unexpected error creating table {table_name}: {e}")

    def budget_table(self, table_name: str):
        return self.client.table(table_name)
