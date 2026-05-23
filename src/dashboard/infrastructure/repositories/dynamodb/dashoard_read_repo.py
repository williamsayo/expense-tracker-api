from datetime import date
import logging
from typing import Any, Dict, cast
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
from src.dashboard.infrastructure.adapters.dto.dashboard import DashboardReadModel
from src.dashboard.infrastructure.repositories.schema import (
    BudgetItem,
    ExpenseItem,
    OverviewItem,
)

settings = get_settings()


class DynamoDbReadRepository(AsyncReadRepository[DashboardReadModel]):

    client: DynamoDBServiceResource
    table: Table

    overview_prefix = "overview"
    expense_prefix = "expenses"
    budget_prefix = "budget"
    insights_prefix = "insights"

    def __init__(self, client: DynamoDBServiceResource, table: Table):
        self.client = client
        self.table = table

    async def get_by_id(
        self, aggregate_id: str | UUID, *, sort_key: str | None = None
    ) -> Either[
        DashboardReadModel, RepositoryNotFoundError | RepositoryUnexpectedError
    ]:
        if sort_key is None:
            sort_key = f"{self.overview_prefix}#{date.today().isoformat()}"

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
                        message=f"Item with ID {aggregate_id} not found."
                    )
                )

            overview_item = cast(OverviewItem, dynamo_item)

            read_model = DashboardReadModel(**overview_item)  # type: ignore

            return result_ok(read_model)

        except Exception as error:
            return result_fail(RepositoryUnexpectedError(error))

    async def get_expenses_projection(
        self, user_id: str, aggregate_id: str | UUID, *, sort_key: str | None = None
    ) -> Either[list[ExpenseItem], RepositoryUnexpectedError]:
        try:
            response = await self.table.query(
                KeyConditionExpression=Key("user_id").eq(user_id)
                & Key("sk").begins_with(f"{self.expense_prefix}#{aggregate_id}"),
            )

            items = response["Items"]
            expenses = cast(list[ExpenseItem], items)

            return result_ok(expenses)

        except Exception as error:
            return result_fail(RepositoryUnexpectedError(error))

    async def get_budgets_projection(
        self, user_id: str, aggregate_id: str | UUID, *, sort_key: str | None = None
    ) -> Either[list[BudgetItem], RepositoryUnexpectedError]:
        try:
            response = await self.table.query(
                KeyConditionExpression=Key("user_id").eq(user_id)
                & Key("sk").eq(f"{self.budget_prefix}#{aggregate_id}"),
            )
            items = response["Items"]

            return result_ok(cast(list[BudgetItem], items))

        except Exception as error:
            return result_fail(RepositoryUnexpectedError(error))

    async def add(
        self, aggregate: DashboardReadModel, *, sort_key: str | None = None
    ) -> Either[None, ConflictError | ConcurrencyError | RepositoryUnexpectedError]:

        if sort_key is None:
            sort_key = self.overview_prefix

        try:
            await self.table.put_item(
                Item={
                    "user_id": aggregate.user_id,
                    "sk": sort_key,
                    **aggregate.model_dump(),
                }
            )
            return result_ok(None)
        except Exception as error:
            return result_fail(RepositoryUnexpectedError(error))

    async def add_expense(
        self, user_id: str, aggregate: ExpenseItem
    ) -> Either[None, RepositoryUnexpectedError]:
        try:
            exists = await self.exists(
                user_id, sort_key=f"{self.expense_prefix}#{aggregate['id']}"
            )

            if is_fail(exists):
                return result_fail(exists.value)

            if exists.value:
                await self.table.update_item(
                    Key={
                        "user_id": user_id,
                        "sk": f"{self.expense_prefix}#{aggregate['id']}",
                    },
                    UpdateExpression="SET expenses = list_append(if_not_exists(expenses, :empty_list), :expense)",
                    ExpressionAttributeValues={
                        ":expense": aggregate,
                        ":empty_list": [],
                    },
                    ReturnValues="UPDATED_NEW",
                )
            else:
                await self.table.put_item(
                    Item={
                        "user_id": user_id,
                        "sk": f"{self.expense_prefix}#{aggregate['id']}",
                        **(cast(Dict[str, Any], aggregate)),
                    }
                )
            return result_ok(None)
        except Exception as error:
            return result_fail(RepositoryUnexpectedError(error))

    async def add_Budget(
        self, user_id: str, aggregate: BudgetItem
    ) -> Either[None, RepositoryUnexpectedError]:
        try:
            exists = await self.exists(
                user_id, sort_key=f"{self.budget_prefix}#{aggregate['id']}"
            )

            if is_fail(exists):
                return result_fail(exists.value)

            if exists.value:
                await self.table.update_item(
                    Key={
                        "user_id": user_id,
                        "sk": f"{self.budget_prefix}#{aggregate['id']}",
                    },
                    UpdateExpression="SET expenses = list_append(if_not_exists(expenses, :empty_list), :expense)",
                    ExpressionAttributeValues={
                        ":expense": aggregate,
                        ":empty_list": [],
                    },
                    ReturnValues="UPDATED_NEW",
                )
            else:
                await self.table.put_item(
                    Item={
                        "user_id": user_id,
                        "sk": f"{self.budget_prefix}#{aggregate['id']}",
                        **(cast(Dict[str, Any], aggregate)),
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
        DashboardReadModel,
        RepositoryUnexpectedError | DataIntegrityError | RepositoryNotFoundError,
    ]: ...  # Implement if needed, otherwise can be left unimplemented or raise NotImplementedError

    async def list(
        self, options: GetOptions[Any]
    ) -> Either[
        list[DashboardReadModel], RepositoryUnexpectedError | DataIntegrityError
    ]: ...  # Implement if needed, otherwise can be left unimplemented or raise NotImplementedError

    async def remove(
        self, aggregate: DashboardReadModel, *, sort_key: str | None = None
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
