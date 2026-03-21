from fastapi.routing import APIRouter
from fastapi import status, Depends
from typing import List, Annotated
from result import is_fail
from shared.domain.types.category_types import CategoryType
from shared.utils.auth.dependencies import AuthDeps
from budgeting.application.services.budget_service import BudgetService
from budgeting.infrastructure.adapters.dto.budget import (
    BudgetReadModel,
    BudgetUpdateModel,
    BudgetWriteModel,
)
from budgeting.infrastructure.adapters.dto.budget_allocation import (
    BudgetAllocationWriteModel,
)

router = APIRouter(
    prefix="/budget",
    tags=["Budgeting"],
)


@router.post("", response_model=BudgetReadModel, status_code=status.HTTP_201_CREATED)
async def create_budget(
    budget_data: BudgetWriteModel,
    auth: AuthDeps,
    budget_service: Annotated[BudgetService, Depends()],
):
    result = await budget_service.create_budget_usecase(auth.user_id, budget_data)

    if is_fail(result):
        raise result.value

    return BudgetReadModel.from_entity(result.value)


@router.put(
    "/{aggregate_id}", response_model=BudgetReadModel, status_code=status.HTTP_200_OK
)
async def update_budget(
    aggregate_id: str,
    budget_data: BudgetUpdateModel,
    auth: AuthDeps,
    budget_service: Annotated[BudgetService, Depends()],
):
    result = await budget_service.update_budget_usecase(
        aggregate_id, auth.user_id, budget_data
    )

    if is_fail(result):
        raise result.value

    return BudgetReadModel.from_entity(result.value)


@router.put(
    "/{aggregate_id}/allocate",
    response_model=BudgetReadModel,
    status_code=status.HTTP_200_OK,
)
async def add_budget_allocation(
    aggregate_id: str,
    budget_data: BudgetAllocationWriteModel,
    auth: AuthDeps,
    budget_service: Annotated[BudgetService, Depends()],
):
    result = await budget_service.add_budget_allocation_usecase(
        aggregate_id, auth.user_id, budget_data
    )

    if is_fail(result):
        raise result.value

    return BudgetReadModel.from_entity(result.value)


@router.get("", response_model=List[BudgetReadModel], status_code=status.HTTP_200_OK)
async def retrieve_all_budgets(
    auth: Annotated[AuthDeps, Depends()],
    budget_service: Annotated[BudgetService, Depends()],
):
    result = await budget_service.list_budgets_usecase(auth.user_id)

    if is_fail(result):
        raise result.value

    return [BudgetReadModel.from_entity(budget) for budget in result.value]


@router.get(
    "/{aggregate_id}",
    response_model=BudgetReadModel,
    status_code=status.HTTP_200_OK,
)
async def retrieve_budget(
    aggregate_id: str,
    auth: Annotated[AuthDeps, Depends()],
    budget_service: Annotated[BudgetService, Depends()],
):
    result = await budget_service.get_budget_usecase(aggregate_id, auth.user_id)

    if is_fail(result):
        raise result.value

    return BudgetReadModel.from_entity(result.value)


@router.delete(
    "/{aggregate_id}",
    status_code=status.HTTP_204_NO_CONTENT,
)
async def delete_all_expense_by_category(
    aggregate_id: str,
    auth: AuthDeps,
    budget_service: Annotated[BudgetService, Depends()],
):
    result = await budget_service.delete_budget_usecase(aggregate_id, auth.user_id)

    if is_fail(result):
        raise result.value
    
    return None


@router.delete(
    "/{aggregate_id}/allocation/{allocation_id}",
    status_code=status.HTTP_204_NO_CONTENT,
)
async def delete_budget_allocation(
    aggregate_id: str,
    allocation_id: str,
    auth: AuthDeps,
    budget_service: Annotated[BudgetService, Depends()],
):
    result = await budget_service.delete_budget_allocation_usecase(aggregate_id, allocation_id, auth.user_id)

    if is_fail(result):
        raise result.value
    
    return None
