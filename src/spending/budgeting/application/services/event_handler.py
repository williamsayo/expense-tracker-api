from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker
from boilerplate import DomainEvent
from result import is_fail
from src.spending.budgeting.utils.setup_dependencies import get_budget_read_repository
from src.shared.infrastructure.dispatcher.event_bus import EventHandler
from src.shared.domain.types.category_types import CategoryType
from src.shared.domain.types.currency_types import Currency
from src.spending.budgeting.domain.read_models.budget_summary import (
    BudgetSummaryReadModel,
)
from src.spending.budgeting.domain.read_models.allocation_summary import (
    BudgetAllocationSummaryReadModel,
)


class OnExpenseCreated(EventHandler):

    def __init__(self, session: async_sessionmaker[AsyncSession]):
        self.session = session

    async def handle(self, event: DomainEvent) -> None:
        async with self.session() as session:
            repo = get_budget_read_repository(session)

            data = event.payload["data"]
            user_id = data["user_id"]
            expense_date = data["date"]

            budget_result = await repo.first(
                {
                    "filter": {
                        "user_id": user_id,
                        "expense_date": expense_date,
                    }
                }
            )

            if is_fail(budget_result):
                return

            category = CategoryType(data["category"])
            currency = Currency(data["currency"])
            amount = int(data["amount"])

            budget = budget_result.value

            budget.track_expense(
                category=category,
                amount=amount,
                currency=currency,
            )

            await repo.add(budget)


class OnBudgetCreated(EventHandler):

    def __init__(self, session: async_sessionmaker[AsyncSession]):
        self.session = session

    async def handle(self, event: DomainEvent) -> None:
        async with self.session() as session:
            repo = get_budget_read_repository(session)

            data = event.payload["data"]
            user_id = data["user_id"]
            budget_id = data["budget_id"]
            currency = Currency(data["currency"])

            budget_read_model = BudgetSummaryReadModel(
                {
                    "user_id": user_id,
                    "name": data["name"],
                    "currency": currency,
                    "allocations": [
                        BudgetAllocationSummaryReadModel(
                            {
                                "allocation_id": allocation["allocation_id"],
                                "budget_amount": allocation["budget_amount"],
                                "category": allocation["category"],
                                "spent_amount": 0,
                            }
                        )
                        for allocation in data["allocations"]
                    ],
                    "end_date": data["end_date"],
                    "start_date": data["start_date"],
                    "budget_id": budget_id,
                }
            )

            await repo.add(budget_read_model)
