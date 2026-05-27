from datetime import datetime
from typing import TypedDict
from result import Either, is_fail, result_combine, result_fail, result_ok
from uuid import UUID
from boilerplate import (
    CoreError,
    HttpError,
    AsyncCommandUseCase,
)
from src.shared.application.dtos.upload import FileUploadDTO
from src.shared.domain.value_objects.category_value_object import CategoryValueObject
from src.shared.domain.value_objects.media_value_object import MediaValueObject
from src.shared.domain.value_objects.money_value_object import MoneyValueObject
from src.spending.expenses.domain.entities.expense_entity import ExpenseEntity
from src.spending.shared.domain.services.expense_allocation_service import (
    ExpenseAllocationService,
)
from src.spending.shared.utils.setup_dependencies import SpendingDeps


class ExtractExpenseFromReceiptInput(TypedDict):
    user_id: UUID
    receipt: FileUploadDTO


class ExtractExpenseFromReceiptUsecase(
    AsyncCommandUseCase[ExtractExpenseFromReceiptInput, ExpenseEntity]
):

    def __init__(self, deps: SpendingDeps):
        self.deps = deps

    async def execute(
        self,
        input,
    ) -> Either[ExpenseEntity, CoreError | HttpError]:

        user_id = input["user_id"]
        receipt = input["receipt"]

        filename, content_type = receipt.filename, receipt.content_type

        media_result = await self.deps.media_repo.upload_receipt(
            filename,
            receipt.file.file,
            content_type=content_type,
            user_id=user_id.hex,
            original_filename=receipt.original_filename,
        )

        if is_fail(media_result):
            return media_result

        receipt_key = media_result.value

        public_url = self.deps.cdn.generate_url(receipt_key)

        expense_result = await self.deps.llm.extract_receipt_info(
            public_url, content_type=content_type
        )

        if is_fail(expense_result):
            return expense_result

        expense_data = expense_result.value

        amount = MoneyValueObject.cents(expense_data["amount"])
        money_result = MoneyValueObject.create(
            {"amount": amount, "currency": expense_data["currency"]}
        )
        category_result = CategoryValueObject.create({"name": expense_data["category"]})
        receipt_result = MediaValueObject.create(
            {"media_key": receipt_key, "media_url": public_url}
        )

        combined_result = result_combine(
            (money_result, category_result, receipt_result)
        )

        if is_fail(combined_result):
            return result_fail(combined_result.value)

        money, category, receipt = combined_result.value

        entity_result = ExpenseEntity.create(
            {
                "name": expense_data["name"],
                "merchant": expense_data["merchant"],
                "user_id": user_id,
                "category": category,
                "money": money,
                "date": datetime.fromisoformat(expense_data["date"]),
                "note": expense_data["note"],
                "receipt": receipt,
            }
        )

        if is_fail(entity_result):
            return entity_result
        
        print("Extracted expense entity:", entity_result.value.receipt.url)

        return result_ok(entity_result.value)
