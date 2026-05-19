from src.spending.budgeting.domain.entities.budget_entity import BudgetEntity
from src.spending.budgeting.infrastructure.adapters.ports.repository import (
    BudgetRepositoryProtocol,
)
from src.spending.expenses.domain.entities.expense_entity import ExpenseEntity
from boilerplate import (
    RepositoryUnexpectedError,
    DataIntegrityError,
    RepositoryNotFoundError,
)
from result import Either, is_fail, result_ok


class ExpenseAllocationService:
    def __init__(self, budget_repo: BudgetRepositoryProtocol):
        self.budget_repo = budget_repo

    async def allocate_expense_to_budget(self, expense: ExpenseEntity) -> Either[
        BudgetEntity,
        RepositoryUnexpectedError | DataIntegrityError | RepositoryNotFoundError,
    ]:
        budget_result = await self.budget_repo.first(
            {
                "filter": {
                    "user_id": expense.user_id,
                    "start_date": expense.date,
                    "end_date": expense.date,
                }
            }
        )

        if is_fail(budget_result):
            # If no matching budget is found, we can choose to ignore or handle it as needed.
            return budget_result

        budget = budget_result.value

        budget.track_expense(expense.category, expense.money)
        expense.assign_to_budget(budget.id.value)

        return result_ok(budget)
