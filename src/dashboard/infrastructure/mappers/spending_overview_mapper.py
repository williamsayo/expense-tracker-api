from datetime import date

from boilerplate import UniqueEntityId, IllegalArgumentError, BaseMapper
from src.dashboard.domain.read_models.spending_overview_read_model import (
    CategoryReadModel,
    SpendingOverviewReadModel,
    ExpenseReadModel,
    BudgetReadModel,
)
from src.dashboard.infrastructure.repositories.schema import (
    ExpenseItem,
    BudgetItem,
    SpendingOverviewItem,
    CategoryItem,
)


def create_budget(budget_data: BudgetItem | None) -> BudgetReadModel | None:
    return (
        BudgetReadModel(
            id=budget_data["id"],
            name=budget_data["name"],
            start_date=budget_data["start_date"],
            end_date=budget_data["end_date"],
            total_amount=budget_data["total_amount"],
        )
        if budget_data
        else None
    )


def create_expense(expense_data: ExpenseItem | None) -> ExpenseReadModel | None:
    return (
        ExpenseReadModel(
            id=expense_data["id"],
            name=expense_data["name"],
            date=expense_data["date"],
            amount=expense_data["amount"],
            category=expense_data["category"],
            currency=expense_data["currency"],
            merchant=expense_data["merchant"],
        )
        if expense_data
        else None
    )


def create_category(category_data: CategoryItem) -> CategoryReadModel:
    return CategoryReadModel(
        name=category_data["name"],
        amount=category_data["amount"],
    )


class SpendingOverviewMapper(BaseMapper):
    @staticmethod
    def to_persistence(entity: SpendingOverviewReadModel) -> SpendingOverviewItem:
        return {
            "user_id": entity.user_id,
            "period": entity.period,
            "total_spent": entity.total_spent,
            "total_budgeted": entity.total_budgeted,
            "top_expense": (
                {
                    "id": entity.top_expense.id,
                    "name": entity.top_expense.name,
                    "date": entity.top_expense.date,
                    "amount": entity.top_expense.amount,
                    "category": entity.top_expense.category,
                    "currency": entity.top_expense.currency,
                    "merchant": entity.top_expense.merchant,
                }
                if entity.top_expense
                else None
            ),
            "active_budget": (
                {
                    "id": entity.active_budget.id,
                    "name": entity.active_budget.name,
                    "start_date": entity.active_budget.start_date,
                    "end_date": entity.active_budget.end_date,
                    "total_amount": entity.active_budget.total_amount,
                }
                if entity.active_budget
                else None
            ),
            "top_categories": [
                {"name": category.name, "amount": category.amount}
                for category in entity.top_categories
            ],
            "upcoming_budget": (
                {
                    "id": entity.upcoming_budget.id,
                    "name": entity.upcoming_budget.name,
                    "start_date": entity.upcoming_budget.start_date,
                    "end_date": entity.upcoming_budget.end_date,
                    "total_amount": entity.upcoming_budget.total_amount,
                }
                if entity.upcoming_budget
                else None
            ),
        }

    @staticmethod
    def to_read_model(persistence: SpendingOverviewItem) -> SpendingOverviewReadModel:
        return SpendingOverviewReadModel(
            user_id=persistence.get("user_id"),
            period=persistence.get("period", date.today().strftime("%Y-%m")),
            total_spent=persistence.get("total_spent", 0),
            total_budgeted=persistence.get("total_budgeted", 0),
            top_expense=create_expense(persistence.get("top_expense")),
            active_budget=create_budget(persistence.get("active_budget")),
            top_categories=[
                create_category(category) for category in persistence.get("top_categories", [])
            ],
            upcoming_budget=create_budget(persistence.get("upcoming_budget")),
        )
