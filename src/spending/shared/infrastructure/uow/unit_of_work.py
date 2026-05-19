# from boilerplate import UnitOfWork
from boilerplate import RepositoryUnexpectedError
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker
from src.spending.budgeting.infrastructure.adapters.ports.repository import (
    BudgetRepositoryProtocol,
)
from src.spending.budgeting.infrastructure.repositories.postgres.budget_repo import (
    BudgetRepository,
)
from src.spending.expenses.infrastructure.adapters.ports.repository import (
    ExpenseRepositoryProtocol,
)
from src.spending.expenses.infrastructure.repositories.postgres.expense_repo import (
    ExpenseRepository,
)


class SpendingUnitOfWork:
    def __init__(self, session_factory: async_sessionmaker[AsyncSession]):
        self._session_factory = session_factory

    async def __aenter__(self):
        self.session = self._session_factory()
        self.budget_repository: BudgetRepositoryProtocol = BudgetRepository(
            self.session
        )
        self.expense_repository: ExpenseRepositoryProtocol = ExpenseRepository(
            self.session
        )
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        if exc_type:
            await self.session.rollback()
        else:
            await self.commit()

        await self.session.close()

    async def commit(self):
        # Commit the transaction
        try:
            await self.session.commit()
        except Exception as error:
            raise RepositoryUnexpectedError(error, "Failed to commit transaction")

    async def rollback(self):
        # Rollback the transaction
        await self.session.rollback()
