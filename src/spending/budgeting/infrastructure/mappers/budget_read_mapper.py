from typing import List
from src.spending.budgeting.infrastructure.repositories.schema import (
    Budget,
    BudgetAllocation,
)
from src.spending.budgeting.domain.read_models.budget_summary import (
    BudgetSummaryReadModel,
)
from src.spending.budgeting.domain.read_models.allocation_summary import (
    BudgetAllocationSummaryReadModel,
)
from src.spending.expenses.domain.read_models.expense_read_model import ExpenseReadModel
from src.spending.expenses.infrastructure.repositories.schema import Expense


def create_budget_allocation_summary(
    allocations: List[BudgetAllocation],
) -> List[BudgetAllocationSummaryReadModel]:

    result: List[BudgetAllocationSummaryReadModel] = []

    for allocation in allocations:

        result.append(
            BudgetAllocationSummaryReadModel(
                {
                    "allocation_id": allocation.id,
                    "category": allocation.category,
                    "budget_amount": allocation.amount,
                    "spent_amount": allocation.spent_amount,
                }
            )
        )

    return result


def create_budget_expense_summary(
    expenses: List[Expense],
) -> List[ExpenseReadModel]:

    result: List[ExpenseReadModel] = []

    for expense in expenses:
        result.append(
            ExpenseReadModel(
                {
                    "id": expense.id,
                    "name": expense.name,
                    "user_id": expense.user_id,
                    "category": expense.category,
                    "amount": expense.amount,
                    "currency": expense.currency,
                    "date": expense.date,
                    "note": expense.note,
                }
            )
        )

    return result


class BudgetReadMapper:
    """Maps budget summary data between domain and persistence models."""

    @staticmethod
    def to_persistence(read_model: BudgetSummaryReadModel) -> Budget:
        allocations = [
            BudgetAllocation(
                id=allocation.allocation_id,
                category=allocation.category,
                amount=allocation.budget_amount,
                spent_amount=allocation.spent_amount,
            )
            for allocation in read_model.allocations
        ]

        return Budget(
            id=read_model.budget_id,
            name=read_model.name,
            user_id=read_model.user_id,
            start_date=read_model.start_date,
            end_date=read_model.end_date,
            allocations=allocations,
            currency=read_model.currency,
        )

    @staticmethod
    def to_read_model(
        persistence: Budget,
    ) -> BudgetSummaryReadModel:

        allocations_result = create_budget_allocation_summary(persistence.allocations)
        expenses_result = create_budget_expense_summary(persistence.expenses)

        budget_entity = BudgetSummaryReadModel(
            {
                "name": persistence.name,
                "user_id": persistence.user_id,
                "currency": persistence.currency,
                "allocations": allocations_result,
                "end_date": persistence.end_date,
                "start_date": persistence.start_date,
                "budget_id": persistence.id,
                "expenses": expenses_result,
            }
        )

        return budget_entity
