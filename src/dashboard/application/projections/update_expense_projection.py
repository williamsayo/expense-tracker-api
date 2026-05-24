from datetime import date
from typing import TypedDict
from boilerplate import (
    RepositoryUnexpectedError,
    DataIntegrityError,
    RepositoryNotFoundError,
    AsyncCommandUseCase,
    CoreError,
)
from result import Either, is_fail, result_fail, result_ok
from src.dashboard.utils.setup_dependencies import OverviewDeps
from src.dashboard.infrastructure.adapters.dto.dashboard import (
    ExpenseReadModel,
    CategoryReadModel,
    DashboardReadModel,
)
from src.dashboard.infrastructure.adapters.dto.event import ExpenseCreatedEventPayload
from ..services.expenses_maintainer import RecentExpensesListMaintainer


class UpdateExpenseProjectionInput(TypedDict):
    user_id: str
    expense: ExpenseCreatedEventPayload


class UpdateExpenseProjectionUsecase(AsyncCommandUseCase[UpdateExpenseProjectionInput]):

    def __init__(self, deps: OverviewDeps):
        self.deps = deps

    async def execute(self, input: UpdateExpenseProjectionInput) -> Either[
        None,
        CoreError
        | RepositoryNotFoundError
        | RepositoryUnexpectedError
        | DataIntegrityError,
    ]:

        user_id, expense = input["user_id"], input["expense"]
        data = expense.data

        expense_read_model = ExpenseReadModel(
            id=data.expense_id,
            name=data.name,
            merchant=data.merchant,
            amount=data.amount,
            currency=data.currency,
            category=data.category,
            date=data.date.isoformat(),
        )

        category = CategoryReadModel(name=data.category, amount=data.amount)

        result = await self.deps.repository.add_expense(user_id, expense_read_model)

        overview_result = await self.deps.repository.get_by_id(user_id)

        if is_fail(overview_result):
            return result_fail(overview_result.value)

        overview = overview_result.value

        recent_expense_maintainer_service = RecentExpensesListMaintainer()

        recent_expenses = recent_expense_maintainer_service.maintain_recent_expense(
            overview.recent_expenses.copy(), expense_read_model
        )

        top_expense = recent_expense_maintainer_service.rank_top_expense(
            overview.top_expense, expense_read_model
        )

        total_spent = recent_expense_maintainer_service.evaluate_total_spent(
            overview.total_spent, data.amount
        )

        top_category = recent_expense_maintainer_service.maintain_top_categories(
            overview.top_category.copy(), category
        )

        dashboard_overview = overview.model_copy(
            update={
                "total_spent": total_spent,
                "top_expense": top_expense,
                "top_category": top_category,
                "recent_expenses": recent_expenses,
            },
        )

        result = await self.deps.repository.add(
            dashboard_overview, sort_key=f"overview#{date.today().isoformat()}"
        )

        if is_fail(result):
            return result_fail(result.value)

        return result_ok(None)
