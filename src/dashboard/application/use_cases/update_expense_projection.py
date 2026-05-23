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
    BudgetReadModel,
    ExpenseReadModel,
)
from src.dashboard.infrastructure.adapters.dto.event import ExpenseCreatedEventPayload


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

        result = await self.deps.repository.add_expense(user_id=user_id, expense=data)

        overview_result = await self.deps.repository.get_by_id(user_id)

        if is_fail(overview_result):
            return result_fail(overview_result.value)

        overview = overview_result.value

        recent_expenses = overview.recent_expenses.copy()

        expense = ExpenseReadModel(
            name=data.name,
            merchant=data.merchant,  # TODO: add merchant to domain model and mapper
            amount=data.amount,
            currency=data.currency,
            category=data.category,
            date=data.date.isoformat(),
        )

        if len(overview.recent_expenses) >= 10:
            for index, expense in enumerate(overview.recent_expenses):
                if data.date > date.fromisoformat(expense.date):
                    recent_expenses.insert(index, expense)
                    break
        else:
            recent_expenses.append(expense)

        top_expense = overview.top_expense

        if overview.top_expense is None or data.amount > overview.top_expense.amount:
            top_expense = expense

        updated_total_spent = overview.total_spent + data.amount

        top_category = overview.top_category.copy()

        if top_category and data.category in top_category:
            top_category[data.category] += data.amount
        else:
            top_category[data.category] = data.amount

        dashboard_overview = DashboardReadModel(
            user_id=user_id,
            total_spent=updated_total_spent,
            total_budgeted=overview.total_budgeted,
            top_expense=top_expense,
            top_category=top_category,
            recent_expenses=recent_expenses,
            active_budget=overview.active_budget,
        )

        result = await self.deps.repository.add(
            dashboard_overview, sort_key=f"overview#{date.today().isoformat()}"
        )

        result = await self.deps.repository.add_recent_expense(
            user_id=user_id, aggregate=recent_expenses
        )

        if is_fail(result):
            return result_fail(result.value)

        return result_ok(None)
