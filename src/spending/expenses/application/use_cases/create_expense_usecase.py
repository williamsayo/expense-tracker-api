from typing import TypedDict
from result import Either, is_fail, result_combine, result_fail, result_ok
from boilerplate import (
    CoreError,
    HttpError,
    AsyncCommandUseCase,
    UniqueEntityId,
)
from src.shared.domain.types.user_id import UserId
from src.shared.domain.value_objects.category_value_object import CategoryValueObject
from src.shared.domain.value_objects.money_value_object import MoneyValueObject
from src.spending.expenses.domain.entities.expense_entity import ExpenseEntity
from src.spending.expenses.infrastructure.adapters.dto.expense import ExpenseWriteModel
from src.spending.expenses.utils.setup_dependencies import ExpenseDeps
from src.spending.shared.domain.services.expense_allocation_service import (
    ExpenseAllocationService,
)
from src.spending.shared.utils.setup_dependencies import SpendingDeps


class CreateExpenseInput(TypedDict):
    auth_id: UserId
    expense_data: ExpenseWriteModel


class CreateExpenseUsecase(AsyncCommandUseCase[CreateExpenseInput, UniqueEntityId]):

    def __init__(self, deps: ExpenseDeps):
        self.deps = deps

    async def execute(
        self,
        input: CreateExpenseInput,
    ) -> Either[UniqueEntityId, CoreError | HttpError]:
        auth_id = input["auth_id"]
        expense_data = input["expense_data"]

        amount = MoneyValueObject.to_amount(expense_data.amount)
        money_result = MoneyValueObject.create(
            {"amount": amount, "currency": expense_data.currency}
        )
        category_result = CategoryValueObject.create({"name": expense_data.category})

        combined_result = result_combine((money_result, category_result))

        if is_fail(combined_result):
            return result_fail(combined_result.value)

        money, category = combined_result.value

        entity_result = ExpenseEntity.create(
            {
                "name": expense_data.name,
                "auth_id": auth_id,
                "category": category,
                "money": money,
                "date": expense_data.date,
                "note": expense_data.note,
            }
        )

        # expense_allocation_domain_service = ExpenseAllocationService(
        #     self.deps.uow.budget_repository
        # )

        # budget_result = (
        #     await expense_allocation_domain_service.allocate_expense_to_budget(
        #         entity_result.value
        #     )
        # )

        result = await self.deps.expense_repo.add(entity_result.value)

        if is_fail(result):
            return result

        # if not is_fail(budget_result):
        #     await self.deps.uow.budget_repository.add(budget_result.value)

        # await self.deps.uow.commit()

        return result_ok(entity_result.value.id)
