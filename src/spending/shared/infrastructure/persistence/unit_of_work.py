from typing import Any

from sqlalchemy.ext.asyncio import AsyncSession
from src.spending.budgeting.infrastructure.repositories.dynamodb.budget_repo import (
    BudgetRepository,
)
from src.spending.expenses.infrastructure.repositories.dynamodb.expense_repo import (
    ExpenseRepository,
)


class SpendingUnitOfWork:
    def __init__(self, session_factory: Any):
        self.session = session_factory
        self.budget_repository = BudgetRepository(session_factory)
        self.expense_repository = ExpenseRepository(session_factory)

    async def __aenter__(self):
        # Initialize resources, e.g., database connection
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        # Clean up resources, e.g., close database connection
        await self.rollback()

    async def commit(self):
        # Commit the transaction
        await self.session.commit()

    async def rollback(self):
        # Rollback the transaction
        await self.session.rollback()
