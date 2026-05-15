from boilerplate import CoreError
from uuid import UUID
from result import Either, is_fail, result_ok, result_fail
from src.shared.domain.types.user_id import UserId
from boilerplate import (
    RepositoryUnexpectedError,
    DataIntegrityError,
    RepositoryNotFoundError,
    AuthenticationError,
)
from src.spending.budgeting.infrastructure.mappers.budget_mapper import (
    create_unique_entity_id,
)
from src.spending.budgeting.domain.read_models.budget_summary import (
    BudgetSummaryReadModel,
)
from src.spending.budgeting.utils.setup_dependencies import BudgetReadDeps


class GetBudgetUsecase:
    def __init__(self, deps: BudgetReadDeps):
        self.deps = deps

    async def execute(self, aggregate_id: str, auth_id: UUID) -> Either[
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
        
        if budget.auth_id != auth_id:
            return result_fail(
                AuthenticationError("Unauthorized to access this budget.")
            )

        return result_ok(budget)
