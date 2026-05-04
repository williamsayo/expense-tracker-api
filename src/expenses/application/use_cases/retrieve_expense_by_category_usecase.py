from typing import Sequence
from result import Either, is_fail, result_ok
from boilerplate import (
    RepositoryUnexpectedError,
    DataIntegrityError,
    RepositoryNotFoundError,
    IQueryUseCase,
)
from shared.domain.types.user_id import UserId
from shared.domain.types.category_types import CategoryType
from expenses.domain.read_models.expense_read_model import ExpenseReadModel
from expenses.utils.setup_dependencies import ExpenseReadDeps


class GetExpenseByCategoryUsecase(IQueryUseCase[UserId, ExpenseReadModel]):
    def __init__(self, deps: ExpenseReadDeps):
        self.deps = deps

    async def execute(self, category: CategoryType, user_id: UserId) -> Either[
        Sequence[ExpenseReadModel],
        RepositoryNotFoundError | RepositoryUnexpectedError | DataIntegrityError,
    ]:
        print(category, user_id)
        result = await self.deps.repo.list(
            {"filter": {"category": category.value, "user_id": user_id}, "limit": 20}
        )

        if is_fail(result):
            return result

        return result_ok(result.value)
