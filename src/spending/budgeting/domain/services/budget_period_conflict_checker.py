from result import Either, is_fail, result_fail, result_ok
from boilerplate import CoreError, DomainRuleError
from spending.budgeting.domain.value_objects.budget_period_value_object import (
    BudgetPeriodValueObject,
)
from spending.budgeting.infrastructure.adapters.ports.repository import (
    BudgetRepositoryProtocol,
)
from shared.domain.types.user_id import UserId


class BudgetPeriodConflictError(Exception):
    """Custom error to indicate a conflict when creating a budget for a period that already has a budget."""


class BudgetPeriodConflictChecker:
    def __init__(self, budget_repository: BudgetRepositoryProtocol):
        self.repo = budget_repository

    async def ensureNoBudgetExistsForPeriod(
        self, period: BudgetPeriodValueObject, user_id: UserId
    ) -> Either[None, DomainRuleError | CoreError]:
        existing_budget = await self.repo.list(
            {
                "filter": {
                    "user_id": user_id,
                    "start_date": period.start_date,
                    "end_date": period.end_date,
                }
            }
        )

        if is_fail(existing_budget):
            return existing_budget

        if existing_budget.value:
            return result_fail(
                DomainRuleError(
                    BudgetPeriodConflictError(
                        "A budget exists for the specified period. Cannot create a new budget for this period."
                    ),
                    "A budget exists for the specified period. Cannot create a new budget for this period.",
                )
            )

        return result_ok(None)
