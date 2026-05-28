import asyncio
import dataclasses
from datetime import date
from typing import TypedDict
from boilerplate import (
    RepositoryUnexpectedError,
    DataIntegrityError,
    RepositoryNotFoundError,
    CoreError,
)
from result import Either, is_fail, result_fail, result_ok, result_combine
from src.dashboard.application.services.spending_overview_service import (
    CreateSpendingOverviewService,
)
from src.dashboard.utils.setup_dependencies import OverviewDeps
from src.dashboard.domain.read_models.spending_overview_read_model import (
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
        current_period = date.today().strftime("%Y-%m")

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

        expense_projection_result = await self.apply_expense_projection(
            user_id, expense_read_model
        )

        overview_result = await self.deps.repository.get_by_id(user_id)

        # create spending overview if there is no existing overview for the specified period. This happens because for a new month, the first event that comes in is often an expense creation, and we want to make sure to create the overview for that month so that the expense projection can be applied to it.
        if is_fail(overview_result):
            spending_overview_service = CreateSpendingOverviewService(
                self.deps.repository
            )
            spending_overview_result = await spending_overview_service.execute(user_id)

            if is_fail(spending_overview_result):
                return result_fail(spending_overview_result.value)

            overview_result = spending_overview_result

        recent_financials_result = await self.deps.repository.get_recent_financials(user_id)

        combined_result = result_combine(
            (expense_projection_result, overview_result, recent_financials_result)
        )

        if is_fail(combined_result):
            return result_fail(combined_result.value)

        _, overview, recent_financials = combined_result.value

        expense_projection_service = ExpenseProjectionApplierService()

        recent_expenses = expense_projection_service.update_recent_expenses(
            recent_financials.recent_expenses.copy(), expense_read_model
        )

        top_expense = expense_projection_service.determine_top_expense(
            overview.top_expense, expense_read_model
        )

        total_spent = expense_projection_service.increment_total_spent(
            overview.total_spent, data.amount
        )

        top_category = expense_projection_service.update_top_categories(
            overview.top_categories.copy(), category
        )

        dashboard_overview = dataclasses.replace(
            overview,
            total_spent=total_spent,
            top_expense=top_expense,
            top_categories=top_category,
            period=current_period,
        )

        recent_financials_overview = dataclasses.replace(recent_financials, recent_expenses=recent_expenses)

        result = await asyncio.gather(
            self.deps.repository.add(
                dashboard_overview, sort_key=f"overview#{current_period}"
            ),
            self.deps.repository.add(recent_financials_overview, sort_key=f"recents"),
        )

        combined_result = result_combine(result)

        if is_fail(combined_result):
            return result_fail(combined_result.value)

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
