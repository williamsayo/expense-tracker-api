from typing import List
from uuid import UUID
from boilerplate import (
    AuthenticationError,
    RepositoryUnexpectedError,
    DataIntegrityError,
    CoreError,
)
from result import is_fail, result_ok, result_fail, Either, result_combine

from src.shared.domain.types.user_id import UserId
from src.spending.budgeting.utils.setup_dependencies import BudgetDeps
from src.spending.budgeting.infrastructure.adapters.dto.budget_allocation import (
    BudgetAllocationWriteModel,
)
from src.spending.budgeting.infrastructure.mappers.budget_mapper import (
    create_unique_entity_id,
)
from src.spending.budgeting.domain.entities.budget_entity import BudgetEntity
from src.spending.budgeting.domain.entities.budget_allocation_entity import (
    BudgetAllocationEntity,
)
from src.spending.budgeting.domain.value_objects.amount_value_object import (
    AmountValueObject,
)
from src.shared.domain.value_objects.category_value_object import CategoryValueObject


class AddBudgetAllocationUsecase:

    def __init__(self, deps: BudgetDeps):
        self.deps = deps

    async def execute(
        self,
        aggregate_id: str,
        auth_id: UUID,
        allocation_data: BudgetAllocationWriteModel,
    ) -> Either[
        BudgetEntity,
        CoreError
        | RepositoryUnexpectedError
        | DataIntegrityError
        | AuthenticationError,
    ]:
        """Adds a new allocation to an existing budget."""
        entity_id = create_unique_entity_id(aggregate_id)

        category_result = CategoryValueObject.create({"name": allocation_data.category})
        money_result = AmountValueObject.create(
            {"amount": AmountValueObject.to_amount(allocation_data.amount)}
        )

        combined_result = result_combine((entity_id, category_result, money_result))

        if is_fail(combined_result):
            return result_fail(combined_result.value)

        entity_id, category, amount = combined_result.value

        allocation_result = BudgetAllocationEntity.create(
            {"category": category, "amount": amount}
        )

        if is_fail(allocation_result):
            return result_fail(allocation_result.value)

        budget_result = await self.deps.repo.get_by_id(entity_id)

        if is_fail(budget_result):
            return result_fail(budget_result.value)

        budget_entity = budget_result.value

        if budget_entity.auth_id != auth_id:
            return result_fail(
                AuthenticationError("Unauthorized to modify this budget.")
            )

        result = budget_entity.allocate_budget(allocation_result.value)

        if is_fail(result):
            return result_fail(result.value)

        update_result = await self.deps.repo.add(budget_entity)

        if is_fail(update_result):
            return result_fail(update_result.value)

        return result_ok(budget_entity)
