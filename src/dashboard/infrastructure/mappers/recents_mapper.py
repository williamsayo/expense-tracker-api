from boilerplate import BaseMapper
from src.dashboard.domain.read_models.recents_read_model import RecentsReadModel
from src.dashboard.domain.read_models.spending_overview_read_model import (
    ExpenseReadModel,
    BudgetReadModel,
)
from src.dashboard.infrastructure.repositories.schema import (
    ExpenseItem,
    BudgetItem,
    RecentsItem,
)


def create_recent_expenses(
    recent_expenses_data: list[ExpenseItem],
) -> list[ExpenseReadModel]:
    return [
        ExpenseReadModel(
            name=expense_data["name"],
            id=expense_data["id"],
            date=expense_data["date"],
            amount=expense_data["amount"],
            category=expense_data["category"],
            currency=expense_data["currency"],
            merchant=expense_data["merchant"],
        )
        for expense_data in recent_expenses_data
    ]


def create_recent_budgets(
    recent_budgets_data: list[BudgetItem],
) -> list[BudgetReadModel]:
    return [
        BudgetReadModel(
            name=budget_data["name"],
            id=budget_data["id"],
            start_date=budget_data["start_date"],
            end_date=budget_data["end_date"],
            total_amount=budget_data["total_amount"],
        )
        for budget_data in recent_budgets_data
    ]


class RecentsMapper(BaseMapper):
    @staticmethod
    def to_persistence(entity: RecentsReadModel) -> RecentsItem:
        return {
            "user_id": entity.user_id,
            "recent_expenses": [
                {
                    "id": expense.id,
                    "name": expense.name,
                    "date": expense.date,
                    "amount": expense.amount,
                    "category": expense.category,
                    "currency": expense.currency,
                    "merchant": expense.merchant,
                }
                for expense in entity.recent_expenses
            ],
            "recent_budgets": [
                {
                    "id": budget.id,
                    "name": budget.name,
                    "start_date": budget.start_date,
                    "end_date": budget.end_date,
                    "total_amount": budget.total_amount,
                }
                for budget in entity.recent_budgets
            ],
        }

    @staticmethod
    def to_read_model(persistence: RecentsItem) -> RecentsReadModel:
        return RecentsReadModel(
            user_id=persistence.get("user_id"),
            recent_expenses=create_recent_expenses(persistence.get("recent_expenses", [])),
            recent_budgets=create_recent_budgets(persistence.get("recent_budgets", [])),
        )
