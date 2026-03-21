from fastapi.routing import APIRouter
from fastapi import status, Depends
from typing import List, Annotated
from result import is_fail
from shared.domain.types.category_types import CategoryType
from shared.utils.auth.dependencies import AuthDeps
from expenses.application.services.expense_service import ExpenseService
from expenses.infrastructure.adapters.dto.expense import (
    ExpenseReadModel,
    ExpenseUpdateModel,
    ExpenseWriteModel,
)

router = APIRouter(
    prefix="/expense",
    tags=["Expense"],
)


@router.post("", response_model=ExpenseReadModel, status_code=status.HTTP_201_CREATED)
async def create_expense(
    expense_data: ExpenseWriteModel,
    auth: AuthDeps,
    expense_service: Annotated[ExpenseService, Depends()],
):
    result = await expense_service.create_expense_usecase(auth.user_id, expense_data)

    if is_fail(result):
        raise result.value

    return ExpenseReadModel.from_entity(result.value)


@router.put(
    "/{aggregate_id}", response_model=ExpenseReadModel, status_code=status.HTTP_200_OK
)
async def update_expense(
    aggregate_id: str,
    expense_data: ExpenseUpdateModel,
    auth: AuthDeps,
    expense_service: Annotated[ExpenseService, Depends()],
):
    result = await expense_service.update_expense_usecase(
        aggregate_id, auth.user_id, expense_data
    )

    if is_fail(result):
        raise result.value

    return ExpenseReadModel.from_entity(result.value)


@router.get("", response_model=List[ExpenseReadModel], status_code=status.HTTP_200_OK)
async def retrieve_all_expenses(
    auth: Annotated[AuthDeps, Depends()],
    expense_service: Annotated[ExpenseService, Depends()],
):
    result = await expense_service.retrieve_all_expense_usecase(auth.user_id)

    if is_fail(result):
        raise result.value

    return [ExpenseReadModel.from_entity(expense) for expense in result.value]


@router.get(
    "/{aggregate_id}",
    response_model=List[ExpenseReadModel],
    status_code=status.HTTP_200_OK,
)
async def retrieve_expense(
    aggregate_id: str,
    auth: AuthDeps,
    expense_service: Annotated[ExpenseService, Depends()],
):
    result = await expense_service.retrieve_expense_usecase(aggregate_id, auth.user_id)

    if is_fail(result):
        raise result.value

    return ExpenseReadModel.from_entity(result.value)


@router.get(
    "/{category_name}",
    response_model=List[ExpenseReadModel],
    status_code=status.HTTP_200_OK,
)
async def retrieve_expense_by_category(
    category_name: CategoryType,
    auth: AuthDeps,
    expense_service: Annotated[ExpenseService, Depends()],
):
    result = await expense_service.retrieve_expense_by_category_usecase(
        category_name, auth.user_id
    )

    if is_fail(result):
        raise result.value

    return [ExpenseReadModel.from_entity(expense) for expense in result.value]


@router.delete(
    "/{category_name}/expenses",
    status_code=status.HTTP_204_NO_CONTENT,
)
async def delete_all_expense_by_category(
    category_name: CategoryType,
    auth: AuthDeps,
    expense_service: Annotated[ExpenseService, Depends()],
):
    result = await expense_service.delete_expense_by_category_usecase(
        category_name, auth.user_id
    )

    if is_fail(result):
        raise result.value


@router.delete(
    "/{expense_id}",
    status_code=status.HTTP_204_NO_CONTENT,
)
async def delete_expense_by_id(
    expense_id: str,
    auth: AuthDeps,
    expense_service: Annotated[ExpenseService, Depends()],
):
    result = await expense_service.delete_expense_usecase(expense_id, auth.user_id)

    if is_fail(result):
        raise result.value
