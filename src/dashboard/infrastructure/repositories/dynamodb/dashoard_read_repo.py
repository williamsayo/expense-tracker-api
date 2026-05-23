import asyncio
from datetime import date
import logging
from typing import Any, cast
from uuid import UUID
from boilerplate import (
    AsyncReadRepository,
    ConcurrencyError,
    ConflictError,
    GetOptions,
    RepositoryUnexpectedError,
    RepositoryNotFoundError,
)
from boilerplate.errors.repository import DataIntegrityError
from result import Either, is_fail, result_combine, result_fail, result_ok
from src.core.config import get_settings
from src.dashboard.domain.read_models.overview_read_model import (
    DashboardOverviewReadModel,
    ExpenseReadModel,
)
from types_aiobotocore_dynamodb.service_resource import Table, DynamoDBServiceResource
from src.dashboard.infrastructure.repositories.schema import (
    ExpenseSchema,
    SpendingSummarySchema,
)
from dataclasses import asdict

settings = get_settings()


class DynamoDbReadRepository(AsyncReadRepository[DashboardOverviewReadModel]):

    client: DynamoDBServiceResource
    table: Table

    overview_prefix = "overview"
    recent_expenses_prefix = "recent_expenses"
    active_budget_prefix = "active_budget"
    insights_prefix = "insights"

    def __init__(self, client: DynamoDBServiceResource, table: Table):
        self.client = client
        self.table = table

    async def get_by_id(
        self, aggregate_id: str | UUID, *, sort_key: str | None = None
    ) -> Either[
        DashboardOverviewReadModel, RepositoryNotFoundError | RepositoryUnexpectedError
    ]:
        try:
            # get spending summary and recent expenses in parallel
            response = await asyncio.gather(
                self.table.get_item(
                    Key={
                        "user_id": str(aggregate_id),
                        "sk": f"{self.overview_prefix}#{date.today().isoformat()}",
                    }
                ),
                self.table.get_item(
                    Key={
                        "user_id": str(aggregate_id),
                        "sk": self.recent_expenses_prefix,
                    }
                ),
            )

            spending_summary, recent_expenses = response

            spending_summary_item = spending_summary.get("Item", None)
            recent_expenses_item = recent_expenses.get("Item", None)

            if spending_summary_item is None or recent_expenses_item is None:
                return result_fail(
                    RepositoryNotFoundError(message=f"User Overview not found.")
                )

            spending_summary_item.pop("recent_expenses", None)

            read_model = DashboardOverviewReadModel(
                user_id=spending_summary_item['user_id'],
                total_spent=spending_summary_item["total_spent"],
                total_budgeted=spending_summary_item["total_budgeted"],
                top_expense=spending_summary_item["top_expense"],
                top_category=spending_summary_item["top_category"], 
                active_budget=spending_summary_item["active_budget"],
                recent_expenses=recent_expenses_item["expenses"], 
            )  # type: ignore

            return result_ok(read_model)

        except Exception as error:
            return result_fail(RepositoryUnexpectedError(error))

    async def get_recent_expenses(
        self, user_id: str
    ) -> Either[list[ExpenseReadModel], RepositoryUnexpectedError]:
        try:
            response = await self.table.get_item(
                Key={
                    "user_id": user_id,
                    "sk": self.recent_expenses_prefix,
                },
                ProjectionExpression="expenses",
            )
            items = response.get("Item", {})
            recent_expenses = cast(
                list[ExpenseSchema], items.get("expenses", [])
            )

            read_models = [ExpenseReadModel(**expense) for expense in recent_expenses]

            return result_ok(read_models)
        except Exception as error:
            return result_fail(RepositoryUnexpectedError(error))

    async def get_spending_summary(
        self, user_id: str, period: date
    ) -> Either[
        SpendingSummarySchema, RepositoryNotFoundError | RepositoryUnexpectedError
    ]:
        try:
            response = await self.table.get_item(
                Key={
                    "user_id": user_id,
                    "sk": f"{self.overview_prefix}#{period.isoformat()}",
                }
            )
            items = response.get("Item", {})

            return result_ok(cast(SpendingSummarySchema, items))

        except Exception as error:
            return result_fail(RepositoryUnexpectedError(error))

    async def add(
        self, aggregate: DashboardOverviewReadModel, *, sort_key: str | None = None
    ) -> Either[None, ConflictError | ConcurrencyError | RepositoryUnexpectedError]:

        if sort_key is None:
            sort_key = self.overview_prefix

        try:
            await self.table.put_item(
                Item={
                    "user_id": aggregate.user_id,
                    "sk": sort_key,
                    **asdict(aggregate),
                }
            )
            return result_ok(None)
        except Exception as error:
            return result_fail(RepositoryUnexpectedError(error))

    async def add_recent_expense(
        self, user_id: str, aggregate: list[ExpenseReadModel]
    ) -> Either[None, RepositoryUnexpectedError]:
        try:
            await self.table.put_item(
                Item={
                    "user_id": user_id,
                    "sk": self.recent_expenses_prefix,
                    "expenses": [asdict(expense) for expense in aggregate],
                }
            )
            return result_ok(None)
        except Exception as error:
            return result_fail(RepositoryUnexpectedError(error))

    async def exists(
        self, aggregate_id: str, *, sort_key: str | None = None
    ) -> Either[bool, RepositoryUnexpectedError]:
        sk = {"sk": sort_key} if sort_key else {}

        try:
            response = await self.table.get_item(Key={"user_id": aggregate_id, **sk})
            return result_ok("Item" in response)
        except Exception as error:
            return result_fail(RepositoryUnexpectedError(error))

    @staticmethod
    async def _create_table(table_name: str, client: DynamoDBServiceResource):
        try:
            table = await client.create_table(
                TableName=table_name,
                KeySchema=[
                    {"AttributeName": "user_id", "KeyType": "HASH"},
                    {"AttributeName": "sk", "KeyType": "RANGE"},
                ],
                AttributeDefinitions=[
                    {"AttributeName": "user_id", "AttributeType": "S"},
                    {"AttributeName": "sk", "AttributeType": "S"},
                ],
                ProvisionedThroughput={
                    "ReadCapacityUnits": 5,
                    "WriteCapacityUnits": 5,
                },
            )
            await table.wait_until_exists()
            logging.info(f"Table {table} created successfully.")
            return result_ok(table)
        except (
            client.meta.client.exceptions.ResourceInUseException,
            client.meta.client.exceptions.TableAlreadyExistsException,
        ) as error:
            logging.info(f"Table {table_name} already exists.")
        except Exception as error:
            return result_fail(
                RepositoryUnexpectedError(
                    error, f"Unexpected error creating table {table_name}"
                )
            )

        return result_ok()

    async def first(self, options: GetOptions[Any]) -> Either[
        DashboardOverviewReadModel,
        RepositoryUnexpectedError | DataIntegrityError | RepositoryNotFoundError,
    ]: ...  # Implement if needed, otherwise can be left unimplemented or raise NotImplementedError

    async def list(
        self, options: GetOptions[Any]
    ) -> Either[
        list[DashboardOverviewReadModel], RepositoryUnexpectedError | DataIntegrityError
    ]: ...  # Implement if needed, otherwise can be left unimplemented or raise NotImplementedError

    async def remove(
        self, aggregate: DashboardOverviewReadModel, *, sort_key: str | None = None
    ) -> Either[
        None, RepositoryUnexpectedError | ConcurrencyError | ConflictError
    ]: ...  # Implement if needed, otherwise can be left unimplemented or raise NotImplementedError

    @staticmethod
    async def _get_table(table_name: str, client: DynamoDBServiceResource):
        try:
            table = await client.Table(table_name)
            return result_ok(table)
        except Exception as error:
            return result_fail(RepositoryUnexpectedError(error))

    @classmethod
    async def create(cls, client: DynamoDBServiceResource):
        table = await cls._get_table(settings.dynamodb_dashboard_table_name, client)

        if is_fail(table):
            return result_fail(table.value)

        return result_ok(cls(client, table.value))
