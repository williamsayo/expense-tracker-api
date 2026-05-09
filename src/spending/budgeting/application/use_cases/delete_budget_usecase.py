from boilerplate import (
    AuthenticationError,
    RepositoryUnexpectedError,
    DataIntegrityError,
    CoreError,
)
from result import is_fail, result_ok, result_fail, Either
from src.shared.domain.types.user_id import UserId
from src.spending.budgeting.utils.setup_dependencies import BudgetDeps
from src.spending.budgeting.infrastructure.mappers.budget_mapper import (
    create_unique_entity_id,
)


class DeleteBudgetUsecase:
    def __init__(self, deps: BudgetDeps):
        self.deps = deps

    async def execute(self, aggregate_id: str, user_id: UserId) -> Either[
        None,
        CoreError
        | RepositoryUnexpectedError
        | DataIntegrityError
        | AuthenticationError,
    ]:
        """Deletes a budget."""
        entity_id = create_unique_entity_id(aggregate_id)

        if is_fail(entity_id):
            return result_fail(entity_id.value)

        budget_result = await self.deps.repo.get_by_id(entity_id.value)

        if is_fail(budget_result):
            return result_fail(budget_result.value)

        budget_entity = budget_result.value

        if budget_entity.user_id != user_id:
            return result_fail(
                AuthenticationError("Unauthorized to delete this budget.")
            )

        result = await self.deps.repo.remove(budget_result.value)

        if is_fail(result):
            return result

        return result_ok()
