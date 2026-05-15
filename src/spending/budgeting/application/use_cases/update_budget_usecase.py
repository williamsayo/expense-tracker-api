from uuid import UUID
from boilerplate import (
    AuthenticationError,
    IllegalArgumentError,
    RepositoryUnexpectedError,
    DataIntegrityError,
    CoreError,
)
from result import is_fail, result_ok, result_fail, Either
from src.spending.budgeting.utils.setup_dependencies import BudgetDeps
from src.spending.budgeting.infrastructure.adapters.dto.budget import BudgetUpdateModel
from src.spending.budgeting.domain.entities.budget_entity import BudgetEntity
from src.spending.budgeting.infrastructure.mappers.budget_mapper import (
    create_unique_entity_id,
)


class UpdateBudgetUsecase:
    def __init__(self, deps: BudgetDeps):
        self.deps = deps

    async def execute(
        self, aggregate_id: str, auth_id: UUID, budget_data: BudgetUpdateModel
    ) -> Either[
        BudgetEntity,
        CoreError
        | RepositoryUnexpectedError
        | DataIntegrityError
        | AuthenticationError,
    ]:
        """Updates an existing budget."""
        entity_id = create_unique_entity_id(aggregate_id)

        if is_fail(entity_id):
            return result_fail(entity_id.value)

        budget_result = await self.deps.repo.get_by_id(entity_id.value)

        if is_fail(budget_result):
            return result_fail(budget_result.value)

        budget_entity = budget_result.value

        if budget_entity.auth_id != auth_id:
            return result_fail(
                AuthenticationError("Unauthorized to update this budget.")
            )

        if budget_data.allocation is not None and budget_data.allocation.id is None:
            return result_fail(IllegalArgumentError(None, "Invalid allocation ID."))

        if budget_data.allocation is not None:
            allocation_id = create_unique_entity_id(budget_data.allocation.id)

            if is_fail(allocation_id):
                return result_fail(allocation_id.value)

            budget_entity.update_allocation(
                allocation_id.value,
                amount=budget_data.allocation.amount,
                category=budget_data.allocation.category,
            )

        budget_entity.change_budget_context(
            currency=budget_data.currency,
            start_date=budget_data.start_date,
            end_date=budget_data.end_date,
        )

        result = await self.deps.repo.add(budget_entity)

        if is_fail(result):
            return result

        return result_ok(budget_entity)
