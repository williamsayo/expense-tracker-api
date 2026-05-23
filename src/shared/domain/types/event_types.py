from enum import StrEnum

class EventTypes(StrEnum):
    EXPENSE_CREATED = "expense.created"
    BUDGET_CREATED = "budget.created"
    USER_CREATED = "user.created"
