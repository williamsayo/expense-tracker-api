import dataclasses
from src.dashboard.domain.read_models.spending_overview_read_model import (
    ExpenseReadModel,
    CategoryReadModel,
)


class ExpenseProjectionApplierService:
    """Service used by the projector to update expense read-model projections.

    This service contains projection-focused helpers that the projector can
    call when applying expense-related events to the read model.
    """

    MAX_RECENT_EXPENSES = 10
    MAX_TOP_CATEGORIES = 5

    def update_recent_expenses(
        self,
        recent_expenses: list[ExpenseReadModel],
        expense: ExpenseReadModel,
    ) -> list[ExpenseReadModel]:
        """Add or re-order a recent expense entry and return the updated list.

        This keeps the most recent expenses first and caps the list at
        `MAX_RECENT_EXPENSES`.
        Args:
            recent_expenses  (list[ExpenseReadModel]): The current list of recent expenses to be updated.
            expense (ExpenseReadModel): The new expense to potentially add or re-order in the recent expenses list.
        Returns:
            list[ExpenseReadModel]: An updated list of recent expenses, ordered by date with the most recent first and capped at `MAX_RECENT_EXPENSES`.

        """

        if len(recent_expenses) < self.MAX_RECENT_EXPENSES:
            recent_expenses.append(expense)
            return recent_expenses

        insert_pos = 0
        for index, recent_expense in enumerate(recent_expenses):
            if expense.date > recent_expense.date:
                insert_pos = index

        recent_expenses.insert(insert_pos, expense)

        return recent_expenses[: self.MAX_RECENT_EXPENSES]

    def determine_top_expense(
        self, current_top_expense: ExpenseReadModel | None, expense: ExpenseReadModel
    ) -> ExpenseReadModel:
        """Return the expense that should be considered the top expense.
        Args:
            current_top_expense  (ExpenseReadModel | None): The current top expense to compare against.
            expense (ExpenseReadModel): The new expense to potentially replace the current top expense.
        Returns:
            ExpenseReadModel: The expense that should be considered the top expense after comparison, which could be either the current top expense or the new expense if it has a higher amount.
        """

        if current_top_expense is None or expense.amount > current_top_expense.amount:
            return expense

        return current_top_expense

    def increment_total_spent(self, total_spent: int, amount: int) -> int:
        """Add the given amount to the running total spent.
        Args:
            total_spent (int): The current total spent amount to be updated.
            amount (int): The new expense amount to add to the total spent.
        Returns:
            int: The updated total spent amount after adding the new expense amount.
        """
        return total_spent + amount

    def update_top_categories(
        self, top_categories: list[CategoryReadModel], category: CategoryReadModel
    ) -> list[CategoryReadModel]:
        """Maintain the top categories list ordered by amount.
        Keeps at most `MAX_TOP_CATEGORIES` entries.
        Args:
            top_categories (list[CategoryReadModel]): The current list of top categories to be updated.
            category (CategoryReadModel): The category to potentially add or update in the top categories list.
        Returns:
            list[CategoryReadModel]: An updated list of top categories, ordered by amount and capped at `MAX_TOP_CATEGORIES`.
        """

        identified_category = next(
            (
                current_category
                for current_category in top_categories
                if category.name == current_category.name
            ),
            None,
        )

        if identified_category is not None:
            total_amount = identified_category.amount + category.amount
            category = dataclasses.replace(
                identified_category, amount=total_amount
            )
            top_categories.remove(identified_category)

        top_categories.append(category)

        return top_categories
