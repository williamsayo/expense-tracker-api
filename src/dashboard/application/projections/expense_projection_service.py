from datetime import date
from typing import TypedDict
from boilerplate import (
    RepositoryUnexpectedError,
    DataIntegrityError,
    RepositoryNotFoundError,
    CoreError,
)
from result import Either, is_fail, result_fail, result_ok, result_combine
from src.dashboard.utils.setup_dependencies import OverviewDeps
from src.dashboard.infrastructure.adapters.dto.dashboard import (
    ExpenseReadModel,
    CategoryReadModel,
)
from src.dashboard.infrastructure.adapters.dto.event import ExpenseCreatedEventPayload
from ..services.expense_overview_applier_service import ExpenseProjectionApplierService


class ExpenseProjectionInput(TypedDict):
    user_id: str
    expense: ExpenseCreatedEventPayload


class ExpenseProjectionService:
    def __init__(self, deps: OverviewDeps):
        self.deps = deps

    async def apply_expense_projection(
        self, user_id: str, expense: ExpenseReadModel
    ) -> Either[
        None,
        CoreError
        | RepositoryNotFoundError
        | RepositoryUnexpectedError
        | DataIntegrityError,
    ]:
        expense_projection_result = await self.deps.repository.add_expense(
            user_id, expense
        )

        if is_fail(expense_projection_result):
            return result_fail(expense_projection_result.value)

        return result_ok(None)

    async def update_overview_on_expense_created(
        self, input: ExpenseProjectionInput
    ) -> Either[
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

        expense_projection_result = await self.deps.repository.add_expense(
            user_id, expense_read_model
        )

        overview_result = await self.deps.repository.get_by_id(user_id)

        combined_result = result_combine((expense_projection_result, overview_result))

        if is_fail(combined_result):
            return result_fail(combined_result.value)

        _, overview = combined_result.value

        expense_projection_service = ExpenseProjectionApplierService()

        recent_expenses = expense_projection_service.update_recent_expenses(
            overview.recent_expenses.copy(), expense_read_model
        )

        top_expense = expense_projection_service.determine_top_expense(
            overview.top_expense, expense_read_model
        )

        total_spent = expense_projection_service.increment_total_spent(
            overview.total_spent, data.amount
        )

        top_category = expense_projection_service.update_top_categories(
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
            dashboard_overview, sort_key=f"overview#{date.today().strftime('%Y-%m')}"
        )

        if is_fail(result):
            return result_fail(result.value)

        return result_ok(None)

    async def update_overview_on_expense_updated(
        self, input: ExpenseProjectionInput
    ) -> Either[
        None,
        CoreError
        | RepositoryNotFoundError
        | RepositoryUnexpectedError
        | DataIntegrityError,
    ]:
        # For simplicity, we'll treat an update similar to a creation in this example.
        # In a real-world scenario, you'd want to handle the differences appropriately.
        return await self.update_overview_on_expense_created(input)
