from typing import List
from uuid import UUID
from boilerplate.ports.mappers import BaseMapper
from boilerplate.domain.unique_entity_id import UniqueEntityId
from boilerplate.errors.domain import IllegalArgumentError
from boilerplate.errors.core import CoreError
from result import Either, result_ok, result_fail, is_fail, result_combine
from shared.domain.value_objects.money_value_object import MoneyValueObject
from shared.domain.value_objects.category_value_object import CategoryValueObject
from budgeting.domain.entities.budget_entity import BudgetEntity
from budgeting.domain.entities.budget_allocation_entity import BudgetAllocationEntity
from budgeting.domain.value_objects.budget_period_value_object import (
    BudgetPeriodValueObject,
)
from budgeting.infrastructure.repositories.schema import Budget, BudgetAllocation


def create_unique_entity_id(
    id: str | UUID,
) -> Either[UniqueEntityId, IllegalArgumentError]:
    try:
        return result_ok(UniqueEntityId(id))
    except Exception as error:
        return result_fail(IllegalArgumentError(error, "Invalid ID"))


def create_budget_allocations(
    allocations: List[BudgetAllocation],
) -> Either[List[BudgetAllocationEntity], CoreError]:
    entities: List[BudgetAllocationEntity] = []

    for allocation in allocations:
        id_result = create_unique_entity_id(allocation.id)

        if is_fail(id_result):
            return result_fail(id_result.value)

        money_result = MoneyValueObject.create(
            {"amount": allocation.amount, "currency": allocation.currency}
        )
        category_result = CategoryValueObject.create({"name": allocation.category})
        combined_result = result_combine((id_result, money_result, category_result))

        if is_fail(combined_result):
            return result_fail(combined_result.value)

        entity_id, money, category = combined_result.value

        allocation = BudgetAllocationEntity.existing_budget_allocation(
            {"money": money, "category": category},
            id=entity_id,
            version=allocation.version,
        )

        if is_fail(allocation):
            return result_fail(allocation.value)

        entities.append(allocation.value)

    return result_ok(entities)


class BudgetMapper(BaseMapper):
    """Maps budget data between domain and persistence models."""

    @staticmethod
    def to_persistence(entity: BudgetEntity) -> Budget:
        allocations = [
            BudgetAllocation(
                id=allocation.id.value,
                category=allocation.category.name,
                amount=allocation.money.amount,
                currency=allocation.money.currency,
                version=allocation.version,
            )
            for allocation in entity.allocations
        ]

        return Budget(
            id=entity.id.value,
            user_id=entity.user_id,
            start_date=entity.budget_period.start_date,
            end_date=entity.budget_period.end_date,
            allocations=allocations,
            version=entity.version,
        )

    @staticmethod
    def to_domain(persistence: Budget) -> Either[BudgetEntity, CoreError]:
        id_result = create_unique_entity_id(persistence.id)

        allocations_result = create_budget_allocations(persistence.allocations)

        budget_period_result = BudgetPeriodValueObject.create(
            {"start_date": persistence.start_date, "end_date": persistence.end_date}
        )
        combined_result = result_combine(
            (id_result, allocations_result, budget_period_result)
        )

        if is_fail(combined_result):
            return result_fail(combined_result.value)

        entity_id, allocations, budget_period = combined_result.value

        budget_entity = BudgetEntity.existing_user_entity(
            {
                "user_id": persistence.user_id,
                "allocations": allocations,
                "budget_period": budget_period,
            },
            id=entity_id,
            version=persistence.version,
        )

        if is_fail(budget_entity):
            return result_fail(budget_entity.value)

        return result_ok(budget_entity.value)
