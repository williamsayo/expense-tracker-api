from typing import List, TypedDict
from boilerplate import (
    AsyncCommandUseCase,
    AsyncCommandUseCase,
    RepositoryUnexpectedError,
    DataIntegrityError,
    CoreError,
    UniqueEntityId,
)
from result import is_fail, result_ok, result_fail, Either, result_combine
from src.shared.domain.types.user_id import UserId
from src.spending.budgeting.utils.setup_dependencies import BudgetDeps
from src.spending.budgeting.infrastructure.adapters.dto.budget import BudgetWriteModel
from src.spending.budgeting.domain.entities.budget_entity import BudgetEntity
from src.spending.budgeting.domain.entities.budget_allocation_entity import (
    BudgetAllocationEntity,
)
from src.spending.budgeting.domain.value_objects.budget_period_value_object import (
    BudgetPeriodValueObject,
)
from src.spending.budgeting.domain.services.budget_period_conflict_checker import (
    BudgetPeriodConflictChecker,
)
from src.spending.budgeting.domain.value_objects.amount_value_object import (
    AmountValueObject,
)
from src.shared.domain.value_objects.category_value_object import CategoryValueObject


class CreateBudgetInput(TypedDict):
    user_id: UserId
    budget_data: BudgetWriteModel


class CreateBudgetUseCase(AsyncCommandUseCase[CreateBudgetInput, UniqueEntityId]):
    def __init__(self, dependency: BudgetDeps) -> None:
        self.deps = dependency

    async def execute(
        self,
        input: CreateBudgetInput,
    ) -> Either[
        UniqueEntityId, CoreError | RepositoryUnexpectedError | DataIntegrityError
    ]:
        """Creates a new budget."""
        user_id = input["user_id"]
        budget_data = input["budget_data"]

        budget_period_result = BudgetPeriodValueObject.create(
            {"start_date": budget_data.start_date, "end_date": budget_data.end_date}
        )

        if is_fail(budget_period_result):
            return result_fail(budget_period_result.value)

        # check if user already has a budget within the given period
        budget_period_checker_domain_service = BudgetPeriodConflictChecker(
            self.deps.repo
        )

        budget_period = budget_period_result.value

        budget_period_check_result = (
            await budget_period_checker_domain_service.ensureNoBudgetExistsForPeriod(
                budget_period, user_id
            )
        )

        if is_fail(budget_period_check_result):
            return budget_period_check_result

        allocations: List[BudgetAllocationEntity] = []

        for allocation in budget_data.allocations:
            category_result = CategoryValueObject.create({"name": allocation.category})
            amount_result = AmountValueObject.create(
                {
                    "amount": AmountValueObject.cents(allocation.amount),
                }
            )

            combined_result = result_combine((category_result, amount_result))

            if is_fail(combined_result):
                return result_fail(combined_result.value)

            category, amount = combined_result.value

            allocation_result = BudgetAllocationEntity.create(
                {"category": category, "amount": amount}
            )

            if is_fail(allocation_result):
                return result_fail(allocation_result.value)

            allocations.append(allocation_result.value)

        budget_entity = BudgetEntity.create(
            {
                "name": budget_data.name,
                "user_id": user_id,
                "allocations": allocations,
                "budget_period": budget_period,
                "currency": budget_data.currency,
            },
        )

        if is_fail(budget_entity):
            return result_fail(budget_entity.value)

        budget = budget_entity.value

        await self.deps.repo.add(budget)

        return result_ok(budget.id)
