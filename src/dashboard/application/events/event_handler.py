from decimal import Decimal
from typing import Any, Self
from boilerplate import EventHandler
from result import is_fail
from types_aiobotocore_dynamodb.service_resource import Table, DynamoDBServiceResource
from ..projections.budget_projection_service import (
    BudgetProjectionService,
)
from ..projections.expense_projection_service import (
    ExpenseProjectionService,
)
from src.dashboard.infrastructure.adapters.dto.event import (
    ExpenseCreatedEventPayload,
    BudgetCreatedEventPayload,
    UserCreatedEventPayload,
)
from src.dashboard.utils.setup_dependencies import OverviewDependency
from ..projections.create_overview_usecase import (
    CreateOverviewUsecase,
)
from src.dashboard.utils.setup_dependencies import get_dashboard_repository
from datetime import date


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

        spending_data: dict[str, Any] = {
            "total_spent": Decimal("0"),
            "total_budgeted": Decimal("0"),
            "top_expense": None,
            "top_categories": [],
            "active_budget": None,
            "upcoming_budget": None,
            "period": date.today().strftime("%Y-%m"),
        }

        recents_data: dict[str, Any] = {
            "recent_expenses": [],
            "recent_budgets": [],
        }

        result = await create_overview_usecase.execute(
            {
                "user_id": user_id,
                "spending_data": spending_data,
                "recents_data": recents_data,
            }
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

        update_expense_projection_usecase = ExpenseProjectionService(deps)

        result = (
            await update_expense_projection_usecase.update_overview_on_expense_created(
                {"user_id": user_id, "expense": event}
            )
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

        update_budget_projection_usecase = BudgetProjectionService(deps)

        result = (
            await update_budget_projection_usecase.update_overview_on_budget_created(
                {"user_id": user_id, "budget": event}
            )
        )

        if is_fail(result):
            raise result.value

        return None

    @classmethod
    async def create(cls, resource: DynamoDBServiceResource, table_name: str) -> Self:
        table = await resource.Table(table_name)
        return cls(resource, table)
