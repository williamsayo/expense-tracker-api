from typing import List
from budgeting.infrastructure.repositories.schema import (
    BudgetAllocationSummary,
    BudgetSummary,
)
from budgeting.domain.read_models.budget_summary import BudgetSummaryReadModel
from budgeting.domain.read_models.allocation_summary import (
    BudgetAllocationSummaryReadModel,
)


def create_budget_allocation_summary(
    allocations: List[BudgetAllocationSummary],
) -> List[BudgetAllocationSummaryReadModel]:

    result: List[BudgetAllocationSummaryReadModel] = []

    for allocation in allocations:
        result.append(
            BudgetAllocationSummaryReadModel(
                props={
                    "allocation_id": allocation.id,
                    "category": allocation.category,
                    "budget_amount": allocation.budget_amount,
                    "spent_amount": allocation.spent_amount,
                }
            )
        )

    return result


class BudgetSummaryMapper:
    """Maps budget summary data between domain and persistence models."""

    @staticmethod
    def to_persistence(read_model: BudgetSummaryReadModel) -> BudgetSummary:
        allocations = [
            BudgetAllocationSummary(
                id=allocation.allocation_id,
                category=allocation.category,
                budget_amount=allocation.budget_amount,
                spent_amount=allocation.spent_amount,
            )
            for allocation in read_model.allocations
        ]

        return BudgetSummary(
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
        persistence: BudgetSummary,
    ) -> BudgetSummaryReadModel:

        allocations_result = create_budget_allocation_summary(persistence.allocations)

        budget_entity = BudgetSummaryReadModel(
            {
                "name": persistence.name,
                "user_id": persistence.user_id,
                "currency": persistence.currency,
                "allocations": allocations_result,
                "end_date": persistence.end_date,
                "start_date": persistence.start_date,
                "budget_id": persistence.id,
            }
        )

        return budget_entity
