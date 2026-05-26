from src.dashboard.infrastructure.adapters.dto.dashboard import (
    BudgetReadModel,
)
from src.dashboard.infrastructure.adapters.dto.event import AllocationEventDataModel
from datetime import date


class BudgetProjectionApplierService:
    """Service used by the projector to update budget read-model projections.

    This service contains projection-focused helpers that the projector can
    call when applying budget-related events to the read model.
    """

    MAX_RECENT_BUDGETS = 5

    def update_recent_budgets(
        self,
        recent_budgets: list[BudgetReadModel],
        budget: BudgetReadModel,
    ) -> list[BudgetReadModel]:
        """Add or re-order a recent expense entry and return the updated list.

        This keeps the most recent expenses first and caps the list at
        `MAX_RECENT_EXPENSES`.
        Args:
            recent_expenses  (list[ExpenseReadModel]): The current list of recent expenses to be updated.
            expense (ExpenseReadModel): The new expense to potentially add or re-order in the recent expenses list.
        Returns:
            list[ExpenseReadModel]: An updated list of recent expenses, ordered by date with the most recent first and capped at `MAX_RECENT_EXPENSES`.

        """

        if len(recent_budgets) >= self.MAX_RECENT_BUDGETS:
            recent_budgets.pop(0)

        recent_budgets.append(budget)
        return recent_budgets[: self.MAX_RECENT_BUDGETS]

    def increment_total_budgeted(self, total_budgeted: int, budget_amount: int) -> int:
        """Add a budget amount to the running total for the projection.
        Args:
            total_budgeted (int): The current total budgeted amount in the projection.
            budget_amount (int): The budget amount to add.
        Returns:
            int: The updated total budgeted amount."""

        return total_budgeted + budget_amount

    def compute_allocations_total(
        self, allocations: list[AllocationEventDataModel]
    ) -> int:
        """Compute the total allocated amount from allocation events."""
        return sum(allocation.budget_amount for allocation in allocations)

    def resolve_active_budget(
        self, active_budget: BudgetReadModel | None, budget: BudgetReadModel
    ) -> BudgetReadModel | None:
        """Determine the active budget based on the current date and the budget's date range.
        Args:
            active_budget (BudgetReadModel | None): The currently active budget, if any.
            budget (BudgetReadModel): The budget being evaluated for activation.
        Returns:
            BudgetReadModel | None: The budget if it is active, otherwise the existing active budget or None.
        """

        if (
            date.fromisoformat(budget.start_date)
            <= date.today()
            <= date.fromisoformat(budget.end_date)
        ):
            return budget

        return active_budget

    def resolve_upcoming_budget(
        self, upcoming_budget: BudgetReadModel | None, budget: BudgetReadModel
    ) -> BudgetReadModel | None:

        current_date = date.today()

        is_future = self._is_future_date(
            current_date, date.fromisoformat(budget.start_date)
        )

        if is_future and upcoming_budget is None:
            return budget

        if (
            upcoming_budget is not None
            and is_future
            and (current_date - date.fromisoformat(budget.start_date))
            <= (current_date - date.fromisoformat(upcoming_budget.start_date))
        ):
            return budget

        return upcoming_budget

    def _is_future_date(self, current_date: date, date: date):
        return date > current_date
