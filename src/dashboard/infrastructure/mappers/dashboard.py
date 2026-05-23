from typing import Any
from boilerplate import UniqueEntityId, IllegalArgumentError, BaseMapper
from domain.entities.example import ExampleEntity
from src.dashboard.domain.read_models.overview_read_model import (
    ExpenseReadModel,
    BudgetReadModel,
    DashboardOverviewReadModel,
)
from src.dashboard.infrastructure.repositories.schema import (
    ExpenseSchema,
    BudgetSchema,
    RecentExpensesSchema,
    SpendingSummarySchema,
)


def create_unique_entity_id(id: str):
    try:
        return UniqueEntityId(id)
    except Exception as error:
        raise IllegalArgumentError(error, "Invalid ID")


def create_recent_expenses(
    recent_expenses_data: list[ExpenseSchema],
) -> list[ExpenseReadModel]:
    return [ExpenseReadModel(**expense_data) for expense_data in recent_expenses_data]

def create_active_budget(active_budget_data: dict | None) -> BudgetReadModel | None:
    return BudgetReadModel(**active_budget_data) if active_budget_data else None


class OverviewMapper(BaseMapper):
    @staticmethod
    def to_persistence(entity: ExampleEntity): ...

    @staticmethod
    def to_read_model(persistence: dict):
        return DashboardOverviewReadModel(
            recent_expenses=create_recent_expenses(
                persistence.get("recent_expenses", [])
            ),
            active_budget=create_active_budget(persistence.get("active_budget")),
        )
