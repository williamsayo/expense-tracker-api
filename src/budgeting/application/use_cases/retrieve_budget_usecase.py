from boilerplate import CoreError
from result import Either, is_fail, result_ok, result_fail
from shared.domain.types.user_id import UserId
from boilerplate import (
    RepositoryUnexpectedError,
    DataIntegrityError,
    RepositoryNotFoundError,
    AuthenticationError
)
from budgeting.infrastructure.mappers.budget_mapper import create_unique_entity_id
from budgeting.domain.read_models.budget_summary import BudgetSummaryReadModel
from budgeting.utils.setup_dependencies import BudgetReadDeps


class GetBudgetUsecase:
    def __init__(self, deps: BudgetReadDeps):
        self.deps = deps

    async def execute(self, aggregate_id: str, user_id: UserId) -> Either[
        BudgetSummaryReadModel,
        CoreError
        | RepositoryNotFoundError
        | RepositoryUnexpectedError
        | DataIntegrityError,
    ]:
        """Retrieves a budget by its ID."""
        entity_id = create_unique_entity_id(aggregate_id)

        if is_fail(entity_id):
            return result_fail(entity_id.value)

        unique_id = entity_id.value

        result = await self.deps.repo.get_by_id(unique_id.value)

        if is_fail(result):
            return result

        budget = result.value
        if budget.user_id != user_id:
            return result_fail(
                AuthenticationError("Unauthorized to access this budget.")
            )

        return result_ok(budget)
