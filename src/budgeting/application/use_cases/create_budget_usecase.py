from fastapi import BackgroundTasks
from typing import List
from boilerplate import (
    RepositoryUnexpectedError,
    DataIntegrityError,
    CoreError,
    IllegalArgumentError,
)
from result import is_fail, result_ok, result_fail, Either, result_combine
from shared.domain.types.user_id import UserId
from budgeting.utils.setup_dependencies import BudgetDeps
from budgeting.infrastructure.adapters.dto.budget import BudgetWriteModel
from budgeting.domain.entities.budget_entity import BudgetEntity
from budgeting.domain.entities.budget_allocation_entity import BudgetAllocationEntity
from budgeting.domain.value_objects.budget_period_value_object import (
    BudgetPeriodValueObject,
)
from budgeting.domain.value_objects.amount_value_object import AmountValueObject
from shared.domain.value_objects.category_value_object import CategoryValueObject


class CreateBudgetUseCase:
    def __init__(self, dependency: BudgetDeps) -> None:
        self.deps = dependency

    async def execute(
        self,
        user_id: UserId,
        budget_data: BudgetWriteModel,
        background_tasks: BackgroundTasks,
    ) -> Either[
        BudgetEntity, CoreError | RepositoryUnexpectedError | DataIntegrityError
    ]:
        """Creates a new budget."""

        # check if user already has a budget within the given period
        existing_budget_entity = await self.deps.repo.first(
            {
                "filter": {
                    "user_id": user_id,
                    "start_date": budget_data.start_date,
                    "end_date": budget_data.end_date,
                }
            }
        )

        if not is_fail(existing_budget_entity):
            return result_fail(
                IllegalArgumentError(
                    None, "A budget already exists for the specified period."
                )
            )

        for allocation in budget_data.allocations:
            allocations: List[BudgetAllocationEntity] = []
            category_result = CategoryValueObject.create({"name": allocation.category})
            amount_result = AmountValueObject.create(
                {
                    "amount": AmountValueObject.to_amount(allocation.amount),
                }
            )

            combined_result = result_combine((category_result, amount_result))

            if is_fail(combined_result):
                return result_fail(combined_result.value)

            category, amount = combined_result.value

            allocation_result = BudgetAllocationEntity.create(
                {"category": category, "amount": amount}
            )

            if is_fail(allocation_result):
                return result_fail(allocation_result.value)

            allocations.append(allocation_result.value)

        budget_period_result = BudgetPeriodValueObject.create(
            {"start_date": budget_data.start_date, "end_date": budget_data.end_date}
        )

        if is_fail(budget_period_result):
            return result_fail(budget_period_result.value)

        budget_entity = BudgetEntity.create(
            {
                "name": budget_data.name,
                "user_id": user_id,
                "allocations": allocations,
                "budget_period": budget_period_result.value,
                "currency": budget_data.currency,
            },
        )

        if is_fail(budget_entity):
            return result_fail(budget_entity.value)

        budget = budget_entity.value

        await self.deps.repo.add(budget)

        # Dispatch uncommitted events after successful persistence
        events = budget.uncommited_events
        background_tasks.add_task(self.deps.dispatcher.publish_all, events)
        budget.uncommit()

        return result_ok(budget)
