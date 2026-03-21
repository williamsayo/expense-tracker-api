from dataclasses import dataclass
from fastapi import Depends
from typing import Annotated
from sqlalchemy.ext.asyncio import AsyncSession
from shared.utils.setup_dependencies import BaseDependency
from shared.infrastructure.db.dependencies import get_session
from expenses.infrastructure.repositories.postgres.expense_repo import ExpenseRepository
from expenses.infrastructure.repositories.base import ExpenseRepositoryProtocol


def get_expense_repo(db: AsyncSession = Depends(get_session)) -> ExpenseRepository:
    return ExpenseRepository(db)


@dataclass(slots=True, frozen=True)
class ExpenseDependencies(BaseDependency):
    """Dependency container for expense use cases."""

    repo: ExpenseRepositoryProtocol = Depends(get_expense_repo)


expense_deps = Annotated[ExpenseDependencies, Depends()]
