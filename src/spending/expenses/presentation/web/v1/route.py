from fastapi.routing import APIRouter
from fastapi import status, Depends, BackgroundTasks
from typing import List, Annotated
from result import is_fail
from src.shared.domain.types.category_types import CategoryType
from src.shared.utils.auth.dependencies import AuthDeps
from src.shared.application.dtos.url_params import UrlParams
from src.spending.expenses.application.services.expense_service import ExpenseService
from src.spending.expenses.application.use_cases.create_expense_usecase import (
    CreateExpenseUsecase,
)
from src.spending.expenses.application.use_cases.retrieve_expense_overview_usecase import (
    GetExpenseOverviewUsecase,
)
from src.spending.expenses.application.use_cases.retrieve_expense_list_usecase import (
    GetExpenseListUsecase,
)
from src.spending.expenses.application.use_cases.retrieve_expense_usecase import (
    GetExpenseUsecase,
)
from src.spending.expenses.application.use_cases.retrieve_expense_by_category_usecase import (
    GetExpenseByCategoryUsecase,
)
from src.spending.expenses.infrastructure.adapters.dto.expense import (
    ExpenseReadModel,
    ExpenseUpdateModel,
    ExpenseWriteModel,
    ExpenseOverviewReadModel,
)

router = APIRouter(
    prefix="/expenses",
    tags=["Expense"],
)

ExpenseUrlParams = Annotated[UrlParams, Depends()]


@router.post("", status_code=status.HTTP_201_CREATED)
async def create_expense(
    expense_data: ExpenseWriteModel,
    auth: AuthDeps,
    use_case: Annotated[CreateExpenseUsecase, Depends()],
):
    result = await use_case.execute(
        {"user_id": auth.user_id, "expense_data": expense_data}
    )

    if is_fail(result):
        raise result.value

    return {"id": result.value.value}


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
    params: ExpenseUrlParams,
    auth: Annotated[AuthDeps, Depends()],
    use_case: Annotated[GetExpenseListUsecase, Depends()],
):
    result = await use_case.execute({"user_id": auth.user_id, "queryParams": params})

    if is_fail(result):
        raise result.value

    return result.value


@router.get(
    "/overview",
    response_model=ExpenseOverviewReadModel,
    status_code=status.HTTP_200_OK,
)
async def expense_overview(
    params: ExpenseUrlParams,
    auth: AuthDeps,
    overview_use_case: Annotated[GetExpenseOverviewUsecase, Depends()],
):
    result = await overview_use_case.execute(auth.user_id, params.page_size)

    if is_fail(result):
        raise result.value

    return result.value


@router.get(
    "/{aggregate_id}",
    response_model=ExpenseReadModel,
    status_code=status.HTTP_200_OK,
)
async def retrieve_expense(
    aggregate_id: str,
    auth: AuthDeps,
    use_case: Annotated[GetExpenseUsecase, Depends()],
):
    result = await use_case.execute(
        {"aggregate_id": aggregate_id, "user_id": auth.user_id}
    )

    if is_fail(result):
        raise result.value

    return result.value


@router.get(
    "/category/{category_name}",
    response_model=List[ExpenseReadModel],
    status_code=status.HTTP_200_OK,
)
async def retrieve_expense_by_category(
    params: ExpenseUrlParams,
    category_name: CategoryType,
    auth: AuthDeps,
    use_case: Annotated[GetExpenseByCategoryUsecase, Depends()],
):
    result = await use_case.execute(
        {"category": category_name, "user_id": auth.user_id}
    )

    if is_fail(result):
        raise result.value

    return result.value


@router.delete(
    "/category/{category_name}",
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
