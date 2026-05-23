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
from src.spending.shared.domain.services.expense_allocation_service import (
    ExpenseAllocationService,
)
from src.spending.shared.utils.setup_dependencies import SpendingDeps


class CreateExpenseInput(TypedDict):
    user_id: UserId
    expense_data: ExpenseWriteModel


class CreateExpenseUsecase(AsyncCommandUseCase[CreateExpenseInput, UniqueEntityId]):

    def __init__(self, deps: SpendingDeps):
        self.deps = deps

    async def execute(
        self,
        input: CreateExpenseInput,
    ) -> Either[UniqueEntityId, CoreError | HttpError]:
        user_id = input["user_id"]
        expense_data = input["expense_data"]

        amount = MoneyValueObject.cents(expense_data.amount)
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
                "user_id": user_id,
                "category": category,
                "money": money,
                "date": expense_data.date,
                "note": expense_data.note,
            }
        )

        async with self.deps.uow as uow:
            expense_allocation_domain_service = ExpenseAllocationService(
                uow.budget_repository
            )

            budget_result = (
                await expense_allocation_domain_service.allocate_expense_to_budget(
                    entity_result.value
                )
            )

            result = await uow.expense_repository.add(
                entity_result.value, auto_commit=False
            )

            if is_fail(result):
                return result

            if not is_fail(budget_result):
                await uow.budget_repository.add(budget_result.value, auto_commit=False)

            events = entity_result.value.uncommited_events
            await self.deps.eventPublisher.dispatch_all(events)

            return result_ok(entity_result.value.id)