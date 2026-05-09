from boilerplate import (
    AuthenticationError,
    RepositoryUnexpectedError,
    DataIntegrityError,
    CoreError,
)
from result import is_fail, result_ok, result_fail, Either, result_combine
from shared.domain.types.user_id import UserId
from spending.budgeting.infrastructure.mappers.budget_mapper import create_unique_entity_id
from spending.budgeting.utils.setup_dependencies import BudgetDeps

class RemoveBudgetAllocationUsecase:
    def __init__(self, deps: BudgetDeps):
        self.deps = deps

    async def execute(
        self, aggregate_id: str, allocation_id: str, user_id: UserId
    ) -> Either[
        None,
        CoreError
        | RepositoryUnexpectedError
        | DataIntegrityError
        | AuthenticationError,
    ]:
        """Deletes a budget allocation."""
        entity_id = create_unique_entity_id(aggregate_id)
        allocation_entity_id = create_unique_entity_id(allocation_id)

        result = result_combine((entity_id, allocation_entity_id))

        if is_fail(result):
            return result_fail(result.value)

        budget_entity_id, allocation_entity_id = result.value

        budget_result = await self.deps.repo.get_by_id(budget_entity_id)

        if is_fail(budget_result):
            return result_fail(budget_result.value)

        budget_entity = budget_result.value

        if budget_entity.user_id != user_id:
            return result_fail(
                AuthenticationError("Unauthorized to delete this budget allocation.")
            )

        result = budget_entity.remove_allocation(allocation_entity_id)

        if is_fail(result):
            return result_fail(result.value)

        result = await self.deps.repo.remove(budget_entity)

        if is_fail(result):
            return result

        return result_ok()
