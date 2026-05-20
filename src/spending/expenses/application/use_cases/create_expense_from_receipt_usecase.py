from typing import TypedDict
from fastapi import UploadFile
from result import Either, is_fail, result_combine, result_fail, result_ok
from uuid import UUID
from boilerplate import (
    CoreError,
    HttpError,
    AsyncCommandUseCase,
    UniqueEntityId,
)
from src.shared.domain.value_objects.category_value_object import CategoryValueObject
from src.shared.domain.value_objects.money_value_object import MoneyValueObject
from src.spending.expenses.domain.entities.expense_entity import ExpenseEntity
from src.spending.shared.domain.services.expense_allocation_service import (
    ExpenseAllocationService,
)
from src.spending.shared.utils.setup_dependencies import SpendingDeps


class CreateExpenseFromReceiptInput(TypedDict):
    user_id: UUID
    receipt: UploadFile


class CreateExpenseFromReceiptUsecase(
    AsyncCommandUseCase[CreateExpenseFromReceiptInput, ExpenseEntity]
):

    def __init__(self, deps: SpendingDeps):
        self.deps = deps

    async def execute(
        self,
        input,
    ) -> Either[ExpenseEntity, CoreError | HttpError]:

        user_id = input["user_id"]
        receipt_file = input["receipt"]

        filename = receipt_file.filename or UUID().hex

        media_result = await self.deps.media_repo.upload_receipt(
            filename, receipt_file.file
        )

        if is_fail(media_result):
            return media_result

        cdn_result = self.deps.cdn.signed_url(media_result.value)

        if is_fail(cdn_result):
            return cdn_result

        expense_result = await self.deps.llm.extract_receipt_info(cdn_result.value)

        if is_fail(expense_result):
            return expense_result

        expense_data = expense_result.value

        amount = MoneyValueObject.cents(expense_data["amount"])
        money_result = MoneyValueObject.create(
            {"amount": amount, "currency": expense_data["currency"]}
        )
        category_result = CategoryValueObject.create({"name": expense_data["category"]})

        combined_result = result_combine((money_result, category_result))

        if is_fail(combined_result):
            return result_fail(combined_result.value)

        money, category = combined_result.value

        entity_result = ExpenseEntity.create(
            {
                "name": expense_data["name"],
                "user_id": user_id,
                "category": category,
                "money": money,
                "date": expense_data["date"],
                "note": expense_data["note"],
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

            return result_ok(entity_result.value)
