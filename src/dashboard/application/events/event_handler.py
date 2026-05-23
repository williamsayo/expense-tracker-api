from decimal import Decimal
from typing import Any, Self
from boilerplate import EventHandler
from result import is_fail
from types_aiobotocore_dynamodb.service_resource import Table, DynamoDBServiceResource
from src.dashboard.application.use_cases.update_overview_projection import (
    UpdateOverviewUsecase,
)
from src.dashboard.application.use_cases.update_spending_summary_usecse import (
    UpdateSpendingSummaryUsecase,
)
from src.dashboard.infrastructure.adapters.dto.dashboard import DashboardWriteModel
from src.dashboard.infrastructure.adapters.dto.event import (
    ExpenseCreatedEventPayload,
    BudgetCreatedEventPayload,
    UserCreatedEventPayload,
)
from src.dashboard.utils.setup_dependencies import OverviewDependency
from ..use_cases.create_overview_usecase import (
    CreateOverviewUsecase,
)
from src.dashboard.utils.setup_dependencies import get_dashboard_repository


class OnUserCreated(EventHandler[UserCreatedEventPayload]):
    def __init__(self, resource: DynamoDBServiceResource, table: Table):
        self.resource = resource
        self.table = table

    async def handle(self, event: UserCreatedEventPayload) -> None:
        event = UserCreatedEventPayload(**event)  # type: ignore
        user_id = event.data.user_id

        dashboard_repository = await get_dashboard_repository(self.resource)

        deps = OverviewDependency(repository=dashboard_repository)

        create_overview_usecase = CreateOverviewUsecase(deps)

        overview_data: dict[str, Any] = {
            "total_spent": Decimal("0"),
            "total_budgeted": Decimal("0"),
            "top_expense": None,
            "top_category": {},
            "recent_expenses": [],
            "active_budget": None,
        }

        result = await create_overview_usecase.execute(
            {"user_id": user_id, "overview_data": overview_data}
        )

        if is_fail(result):
            raise result.value

        return None

    @classmethod
    async def create(cls, resource: DynamoDBServiceResource, table_name: str) -> Self:
        table = await resource.Table(table_name)
        return cls(resource, table)


class OnExpenseCreated(EventHandler[ExpenseCreatedEventPayload]):
    def __init__(self, resource: DynamoDBServiceResource, table: Table):
        self.resource = resource
        self.table = table

    async def handle(self, event: ExpenseCreatedEventPayload) -> None:
        event = ExpenseCreatedEventPayload(**event)  # type: ignore
        data = event.data
        user_id = data.user_id

        dashboard_repository = await get_dashboard_repository(self.resource)

        deps = OverviewDependency(repository=dashboard_repository)

        update_overview_usecase = UpdateOverviewUsecase(deps)

        result = await update_overview_usecase.execute(
            {"user_id": user_id, "expense": event}  # type: ignore #TODO: refactor to use a DTO instead of raw dict
        )

        if is_fail(result):
            raise result.value

        return None

    @classmethod
    async def create(cls, resource: DynamoDBServiceResource, table_name: str) -> Self:
        table = await resource.Table(table_name)
        return cls(resource, table)


class OnBudgetCreated(EventHandler[BudgetCreatedEventPayload]):
    def __init__(self, resource: DynamoDBServiceResource, table: Table):
        self.resource = resource
        self.table = table

    async def handle(self, event: BudgetCreatedEventPayload) -> None:
        event = BudgetCreatedEventPayload(**event)  # type: ignore
        user_id = event.data.user_id

        dashboard_repository = await get_dashboard_repository(self.resource)

        deps = OverviewDependency(repository=dashboard_repository)

        update_spending_summary_usecase = UpdateSpendingSummaryUsecase(deps)

        result = await update_spending_summary_usecase.execute(
            {"user_id": user_id, "budget": event}
        )

        if is_fail(result):
            raise result.value

        return None

    @classmethod
    async def create(cls, resource: DynamoDBServiceResource, table_name: str) -> Self:
        table = await resource.Table(table_name)
        return cls(resource, table)
