import asyncio
from datetime import date
import logging
from typing import Any, cast
from dataclasses import asdict
from uuid import UUID
from boto3.dynamodb.conditions import Key
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
from types_aiobotocore_dynamodb.service_resource import Table, DynamoDBServiceResource
from src.dashboard.infrastructure.adapters.dto.dashboard import (
    DashboardPublicModel,
)
from src.dashboard.domain.read_models.spending_overview_read_model import (
    SpendingOverviewReadModel,
    BudgetReadModel,
    ExpenseReadModel,
)
from src.dashboard.domain.read_models.dashboard_overview_read_model import (
    SpendingInsightReadModel,
)
from src.dashboard.domain.read_models.recent_financials_read_model import RecentFinancialsReadModel
from src.dashboard.infrastructure.mappers.dashboard_mapper import (
    BudgetProjectionMapper,
    ExpenseProjectionMapper,
)
from src.dashboard.infrastructure.mappers.recent_fiancials_mapper import (
    RecentFinancialsMapper,
)
from src.dashboard.infrastructure.mappers.spending_overview_mapper import (
    SpendingOverviewMapper,
)
from src.dashboard.infrastructure.repositories.schema import (
    BudgetProjectionItem,
    ExpenseProjectionItem,
    RecentFinancialsItem,
    SpendingInsightItem,
    SpendingOverviewItem,
)

settings = get_settings()


class DynamoDbReadRepository(AsyncReadRepository[SpendingOverviewReadModel]):

    client: DynamoDBServiceResource
    table: Table

    overview_prefix = "overview"
    expense_prefix = "expenses"
    budget_prefix = "budget"
    insights_prefix = "insights"
    recents_prefix = "recents"

    def __init__(self, client: DynamoDBServiceResource, table: Table):
        self.client = client
        self.table = table

    async def get_by_id(
        self, aggregate_id: str | UUID, *, sort_key: str | None = None
    ) -> Either[
        SpendingOverviewReadModel, RepositoryNotFoundError | RepositoryUnexpectedError
    ]:
        if sort_key is None:
            sort_key = f"{self.overview_prefix}#{date.today().strftime('%Y-%m')}"

        try:
            response = await self.table.get_item(
                Key={
                    "user_id": str(aggregate_id),
                    "sk": sort_key,
                }
            )

            dynamo_item = response.get("Item", None)

            if dynamo_item is None:
                return result_fail(
                    RepositoryNotFoundError(
                        Exception("Overview item not found."),
                        "Overview item not found.",
                    )
                )

            overview_item = cast(SpendingOverviewItem, dynamo_item)

            read_model = SpendingOverviewMapper.to_read_model(overview_item)

            return result_ok(read_model)

        except Exception as error:
            return result_fail(
                RepositoryUnexpectedError(error, "Unexpected error retrieving overview")
            )

    async def get_spending_insight(
        self, user_id: str
    ) -> Either[list[SpendingInsightReadModel], RepositoryUnexpectedError]:
        try:
            response = await self.table.query(
                KeyConditionExpression=Key("user_id").eq(user_id)
                & Key("sk").begins_with(self.overview_prefix),
                ProjectionExpression="period, total_spent, total_budgeted",
            )

            insight_item = cast(list[SpendingInsightItem], response.get("Items", []))

            return result_ok(
                [
                    SpendingInsightReadModel(
                        period=insight["period"],
                        total_spent=insight["total_spent"],
                        total_budgeted=insight["total_budgeted"],
                    )
                    for insight in insight_item
                ]
            )

        except Exception as error:
            return result_fail(
                RepositoryUnexpectedError(error, "Unexpected error retrieving insights")
            )

    async def get_recent_financials(
        self, user_id: str
    ) -> Either[
        RecentFinancialsReadModel, RepositoryUnexpectedError | RepositoryNotFoundError
    ]:
        try:
            response = await self.table.get_item(
                Key={
                    "user_id": user_id,
                    "sk": self.recents_prefix,
                }
            )

            recents_item = cast(RecentFinancialsItem, response.get("Item", None))

            if recents_item is None:
                return result_fail(
                    RepositoryNotFoundError(
                        Exception("Recents item not found."),
                        "Recents item not found.",
                    )
                )

            recents_read_model = RecentFinancialsMapper.to_read_model(recents_item)

            return result_ok(recents_read_model)

        except Exception as error:
            return result_fail(
                RepositoryUnexpectedError(error, "Unexpected error retrieving recents")
            )

    async def get_overview_by_id(
        self, user_id: str, period: date
    ) -> Either[
        DashboardPublicModel, RepositoryNotFoundError | RepositoryUnexpectedError
    ]:
        result = await asyncio.gather(
            self.get_by_id(user_id, sort_key=f"overview#{period.strftime('%Y-%m')}"),
            self.get_spending_insight(user_id),
            self.get_recent_financials(user_id),
        )

        combined_result = result_combine(result)

        if is_fail(combined_result):
            return combined_result

        overview, spending_insights, recent_financials = combined_result.value

        overview_data = SpendingOverviewMapper.to_persistence(overview)

        return result_ok(
            DashboardPublicModel(
                **overview_data,  # type: ignore
                spending_insights=spending_insights,
                recent_expenses=recent_financials.recent_expenses,
                recent_budgets=recent_financials.recent_budgets,
            )
        )

    async def get_expenses_projection(
        self, user_id: str, aggregate_id: str | UUID, *, sort_key: str | None = None
    ) -> Either[list[ExpenseProjectionItem], RepositoryUnexpectedError]:
        try:
            response = await self.table.query(
                KeyConditionExpression=Key("user_id").eq(user_id)
                & Key("sk").begins_with(f"{self.expense_prefix}#{aggregate_id}"),
            )

            items = response["Items"]
            expenses = cast(list[ExpenseProjectionItem], items)

            return result_ok(expenses)

        except Exception as error:
            return result_fail(RepositoryUnexpectedError(error))

    async def get_budgets_projection(
        self, user_id: str, aggregate_id: str | UUID, *, sort_key: str | None = None
    ) -> Either[list[BudgetProjectionItem], RepositoryUnexpectedError]:
        try:
            response = await self.table.query(
                KeyConditionExpression=Key("user_id").eq(user_id)
                & Key("sk").eq(f"{self.budget_prefix}#{aggregate_id}"),
            )
            items = response["Items"]

            return result_ok(cast(list[BudgetProjectionItem], items))

        except Exception as error:
            return result_fail(RepositoryUnexpectedError(error))

    async def add(
        self,
        aggregate: SpendingOverviewReadModel | RecentFinancialsReadModel,
        *,
        sort_key: str | None = None,
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

    async def add_expense(
        self, user_id: str, aggregate: ExpenseReadModel
    ) -> Either[None, RepositoryUnexpectedError]:
        try:
            persistence = ExpenseProjectionMapper.to_persistence(aggregate)
            await self.table.put_item(
                Item=cast(
                    dict[str, Any],
                    {
                        "user_id": user_id,
                        "sk": f"{self.expense_prefix}#{aggregate.id}",
                        **persistence,
                    },
                )
            )
            return result_ok(None)
        except Exception as error:
            return result_fail(RepositoryUnexpectedError(error))

    async def add_Budget(
        self, user_id: str, aggregate: BudgetReadModel
    ) -> Either[None, RepositoryUnexpectedError]:
        try:
            persistence = BudgetProjectionMapper.to_persistence(aggregate)
            await self.table.put_item(
                Item=cast(
                    dict[str, Any],
                    {
                        "user_id": user_id,
                        "sk": f"{self.budget_prefix}#{aggregate.id}",
                        **persistence,
                    },
                )
            )
            return result_ok(None)
        except Exception as error:
            return result_fail(RepositoryUnexpectedError(error))

    async def exists(
        self, aggregate_id: str | UUID, *, sort_key: str | None = None
    ) -> Either[bool, RepositoryUnexpectedError]:
        sk = {"sk": sort_key} if sort_key else {}

        try:
            response = await self.table.get_item(
                Key={"user_id": str(aggregate_id), **sk}
            )
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
        SpendingOverviewReadModel,
        RepositoryUnexpectedError | DataIntegrityError | RepositoryNotFoundError,
    ]: ...  # Implement if needed, otherwise can be left unimplemented or raise NotImplementedError

    async def list(
        self, options: GetOptions[Any]
    ) -> Either[
        list[SpendingOverviewReadModel], RepositoryUnexpectedError | DataIntegrityError
    ]: ...  # Implement if needed, otherwise can be left unimplemented or raise NotImplementedError

    async def remove(
        self, aggregate: SpendingOverviewReadModel, *, sort_key: str | None = None
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
