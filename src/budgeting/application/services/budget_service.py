from typing import List, Sequence
from boilerplate.errors.domain import IllegalArgumentError
from result import result_ok, result_fail, is_fail, result_combine, Either
from boilerplate.errors.http import AuthenticationError
from boilerplate.errors.repository import (
    RepositoryNotFoundError,
    RepositoryUnexpectedError,
    DataIntegrityError,
)
from boilerplate.errors.core import CoreError
from budgeting.infrastructure.mappers.budget_mapper import create_unique_entity_id
from shared.application.services.base import BaseService
from budgeting.utils.setup_dependencies import BudgetDeps
from budgeting.infrastructure.adapters.dto.budget import (
    BudgetWriteModel,
    BudgetUpdateModel,
)
from budgeting.infrastructure.adapters.dto.budget_allocation import (
    BudgetAllocationWriteModel,
)
from budgeting.domain.entities.budget_entity import BudgetEntity
from budgeting.domain.entities.budget_allocation_entity import BudgetAllocationEntity
from budgeting.domain.value_objects.budget_period_value_object import (
    BudgetPeriodValueObject,
)
from shared.domain.types.user_id import UserId
from shared.domain.value_objects.money_value_object import MoneyValueObject
from shared.domain.value_objects.category_value_object import CategoryValueObject


class BudgetService(BaseService[BudgetDeps]):
    """Service layer."""

    def __init__(
        self,
        deps: BudgetDeps,
    ):
        super().__init__(deps)

    async def create_budget_usecase(
        self, user_id: UserId, budget_data: BudgetWriteModel
    ) -> Either[
        BudgetEntity, CoreError | RepositoryUnexpectedError | DataIntegrityError
    ]:
        """Creates a new budget."""
        for allocation in budget_data.allocations:
            allocations: List[BudgetAllocationEntity] = []
            category_result = CategoryValueObject.create({"name": allocation.category})
            money_result = MoneyValueObject.create(
                {
                    "amount": MoneyValueObject.to_amount(allocation.amount),
                    "currency": allocation.currency,
                }
            )

            combined_result = result_combine((category_result, money_result))

            if is_fail(combined_result):
                return result_fail(combined_result.value)

            category, money = combined_result.value

            allocation_result = BudgetAllocationEntity.create(
                {"category": category, "money": money}
            )

            if is_fail(allocation_result):
                return result_fail(allocation_result.value)

            allocations.append(allocation_result.value)

        budget_period_result = BudgetPeriodValueObject.create(
            {"start_date": budget_data.start_date, "end_date": budget_data.end_date}
        )

        if is_fail(budget_period_result):
            return result_fail(budget_period_result.value)

        budget_entity = BudgetEntity.create(
            {
                "user_id": user_id,
                "allocations": allocations,
                "budget_period": budget_period_result.value,
            },
        )

        if is_fail(budget_entity):
            return result_fail(budget_entity.value)

        budget = budget_entity.value

        await self.deps.repo.add(budget)

        return result_ok(budget)

    async def get_budget_usecase(self, aggregate_id: str, user_id: UserId) -> Either[
        BudgetEntity,
        CoreError
        | RepositoryNotFoundError
        | RepositoryUnexpectedError
        | DataIntegrityError,
    ]:
        """Retrieves a budget by its ID."""
        entity_id = create_unique_entity_id(aggregate_id)

        if is_fail(entity_id):
            return result_fail(entity_id.value)

        result = await self.deps.repo.get_by_id(entity_id.value)

        if is_fail(result):
            return result

        budget = result.value
        if budget.user_id != user_id:
            return result_fail(
                AuthenticationError("Unauthorized to access this budget.")
            )

        return result_ok(budget)

    async def list_budgets_usecase(self, user_id: UserId) -> Either[
        Sequence[BudgetEntity],
        CoreError | RepositoryUnexpectedError | DataIntegrityError,
    ]:
        """Lists all budgets."""
        result = await self.deps.repo.list({"filter": {"user_id": user_id}})

        if is_fail(result):
            return result

        return result_ok(result.value)

    async def add_budget_allocation_usecase(
        self,
        aggregate_id: str,
        user_id: UserId,
        allocation_data: BudgetAllocationWriteModel,
    ) -> Either[
        BudgetEntity,
        CoreError
        | RepositoryUnexpectedError
        | DataIntegrityError
        | AuthenticationError,
    ]:
        """Adds a new allocation to an existing budget."""
        entity_id = create_unique_entity_id(aggregate_id)

        category_result = CategoryValueObject.create({"name": allocation_data.category})
        money_result = MoneyValueObject.create(
            {
                "amount": MoneyValueObject.to_amount(allocation_data.amount),
                "currency": allocation_data.currency,
            }
        )

        combined_result = result_combine((entity_id, category_result, money_result))

        if is_fail(combined_result):
            return result_fail(combined_result.value)

        entity_id, category, money = combined_result.value

        allocation_result = BudgetAllocationEntity.create(
            {"category": category, "money": money}
        )

        if is_fail(allocation_result):
            return result_fail(allocation_result.value)

        budget_result = await self.deps.repo.get_by_id(entity_id)

        if is_fail(budget_result):
            return result_fail(budget_result.value)

        budget_entity = budget_result.value

        if budget_entity.user_id != user_id:
            return result_fail(
                AuthenticationError("Unauthorized to modify this budget.")
            )

        result = budget_entity.allocate_budget(allocation_result.value)

        if is_fail(result):
            return result_fail(result.value)

        update_result = await self.deps.repo.add(budget_entity)

        if is_fail(update_result):
            return result_fail(update_result.value)

        return result_ok(budget_entity)

    async def update_budget_usecase(
        self, aggregate_id: str, user_id: UserId, budget_data: BudgetUpdateModel
    ) -> Either[
        BudgetEntity,
        CoreError
        | RepositoryUnexpectedError
        | DataIntegrityError
        | AuthenticationError,
    ]:
        """Updates an existing budget."""
        entity_id = create_unique_entity_id(aggregate_id)

        if is_fail(entity_id):
            return result_fail(entity_id.value)

        budget_result = await self.deps.repo.get_by_id(entity_id.value)

        if is_fail(budget_result):
            return result_fail(budget_result.value)

        budget_entity = budget_result.value

        if budget_entity.user_id != user_id:
            return result_fail(
                AuthenticationError("Unauthorized to update this budget.")
            )

        if budget_data.allocation is not None and budget_data.allocation.id is None:
            return result_fail(IllegalArgumentError(None, "Invalid allocation ID."))

        if budget_data.allocation is not None:
            allocation_id = create_unique_entity_id(budget_data.allocation.id)

            if is_fail(allocation_id):
                return result_fail(allocation_id.value)

            budget_entity.update_allocation(
                allocation_id.value,
                amount=budget_data.allocation.amount,
                currency=budget_data.allocation.currency,
                category=budget_data.allocation.category,
            )

        if budget_data.start_date is not None or budget_data.end_date is not None:
            budget_entity.update_budget_period(
                start_date=budget_data.start_date, end_date=budget_data.end_date
            )

        result = await self.deps.repo.add(budget_entity)

        if is_fail(result):
            return result

        return result_ok(budget_entity)

    async def delete_budget_usecase(self, aggregate_id: str, user_id: UserId) -> Either[
        None,
        CoreError
        | RepositoryUnexpectedError
        | DataIntegrityError
        | AuthenticationError,
    ]:
        """Deletes a budget."""
        entity_id = create_unique_entity_id(aggregate_id)

        if is_fail(entity_id):
            return result_fail(entity_id.value)

        budget_result = await self.deps.repo.get_by_id(entity_id.value)

        if is_fail(budget_result):
            return result_fail(budget_result.value)

        budget_entity = budget_result.value

        if budget_entity.user_id != user_id:
            return result_fail(
                AuthenticationError("Unauthorized to delete this budget.")
            )

        result = await self.deps.repo.remove(budget_result.value)

        if is_fail(result):
            return result

        return result_ok()

    async def delete_budget_allocation_usecase(self, aggregate_id: str, allocation_id: str, user_id: UserId) -> Either[
        None,
        CoreError
        | RepositoryUnexpectedError
        | DataIntegrityError
        | AuthenticationError,
    ]:
        """Deletes a budget allocation."""
        entity_id = create_unique_entity_id(aggregate_id)
        allocation_entity_id = create_unique_entity_id(allocation_id)

        result = result_combine((entity_id, allocation_entity_id))

        if is_fail(result):
            return result_fail(result.value)
        
        budget_entity_id, allocation_entity_id = result.value

        budget_result = await self.deps.repo.get_by_id(budget_entity_id)

        if is_fail(budget_result):
            return result_fail(budget_result.value)

        budget_entity = budget_result.value

        if budget_entity.user_id != user_id:
            return result_fail(
                AuthenticationError("Unauthorized to delete this budget allocation.")
            )

        result = budget_entity.remove_allocation(allocation_entity_id)
        
        if is_fail(result):
            return result_fail(result.value)
        
        # allocation = result.value

        result = await self.deps.repo.remove(budget_entity)

        if is_fail(result):
            return result

        return result_ok()