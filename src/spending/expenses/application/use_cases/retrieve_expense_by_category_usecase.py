from typing import Sequence, TypedDict
from uuid import UUID
from result import Either, is_fail, result_ok
from boilerplate import (
    RepositoryUnexpectedError,
    DataIntegrityError,
    RepositoryNotFoundError,
    AsyncQueryUseCase,
)
from src.shared.domain.types.category_types import Category
from src.spending.expenses.infrastructure.adapters.dto.expense import ExpenseReadModel
from src.spending.expenses.utils.setup_dependencies import ExpenseReadDeps


class GetExpenseByCategoryInput(TypedDict):
    category: Category
    user_id: UUID


class GetExpenseByCategoryUsecase(
    AsyncQueryUseCase[GetExpenseByCategoryInput, Sequence[ExpenseReadModel]]
):
    def __init__(self, deps: ExpenseReadDeps):
        self.deps = deps

    async def execute(self, input: GetExpenseByCategoryInput) -> Either[
        Sequence[ExpenseReadModel],
        RepositoryNotFoundError | RepositoryUnexpectedError | DataIntegrityError,
    ]:
        category = input["category"]
        user_id = input["user_id"]

        print(category, user_id)
        result = await self.deps.repo.list(
            {"filter": {"category": category.value, "user_id": user_id}, "limit": 20}
        )

        if is_fail(result):
            return result

        return result_ok(result.value)
