from boilerplate import BaseMapper
from src.dashboard.domain.read_models.spending_overview_read_model import (
    CategoryReadModel,
    ExpenseReadModel,
    BudgetReadModel,
)
from src.dashboard.infrastructure.repositories.schema import (
    BudgetProjectionItem,
    ExpenseProjectionItem,
    CategoryItem,
)


def create_category(category_data: CategoryItem) -> CategoryReadModel:
    return CategoryReadModel(
        name=category_data["name"],
        amount=category_data["amount"],
    )


class ExpenseProjectionMapper(BaseMapper):
    @staticmethod
    def to_persistence(entity: ExpenseReadModel) -> ExpenseProjectionItem:
        return {
            "id": entity.id,
            "amount": entity.amount,
            "currency": entity.currency,
            "category": entity.category,
            "date": entity.date,
        }

    @staticmethod
    def to_read_model(persistence: ExpenseProjectionItem) -> ExpenseReadModel:
        return ExpenseReadModel(
            id=persistence.get("id"),
            date=persistence.get("date"),
            amount=persistence.get("amount"),
            category=persistence.get("category"),
            currency=persistence.get("currency"),
        )


class BudgetProjectionMapper(BaseMapper):
    @staticmethod
    def to_persistence(entity: BudgetReadModel) -> BudgetProjectionItem:
        return {
            "id": entity.id,
            "total_amount": entity.total_amount,
            "start_date": entity.start_date,
            "end_date": entity.end_date,
            "spent_amount": entity.total_amount,  # Assuming spent_amount is the same as total_amount for projection
        }

    @staticmethod
    def to_read_model(persistence: BudgetProjectionItem) -> BudgetReadModel:
        return BudgetReadModel(
            id=persistence.get("id"),
            start_date=persistence.get("start_date"),
            end_date=persistence.get("end_date"),
            total_amount=persistence.get("total_amount"),
        )


class DashboardOverviewMapper(BaseMapper):
    @staticmethod
    def to_persistence(entity: ...) -> ...: ...

    @staticmethod
    def to_read_model(persistence: ...) -> ...: ...
