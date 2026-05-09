from fastapi.routing import APIRouter
from fastapi import status, Depends
from typing import List, Annotated
from result import is_fail
from src.shared.utils.auth.dependencies import AuthDeps
from src.shared.application.dtos.url_params import UrlParams
from src.spending.budgeting.infrastructure.adapters.dto.budget import (
    BudgetReadModel,
    BudgetUpdateModel,
    BudgetWriteModel,
    BudgetOverviewReadModel,
)
from src.spending.budgeting.infrastructure.adapters.dto.budget_allocation import (
    BudgetAllocationWriteModel,
)
from src.spending.budgeting.application.use_cases.retrieve_budget_usecase import (
    GetBudgetUsecase,
)
from src.spending.budgeting.application.use_cases.retrieve_budget_list_usecase import (
    GetBudgetsUsecase,
)
from src.spending.budgeting.application.use_cases.create_budget_usecase import (
    CreateBudgetUseCase,
)
from src.spending.budgeting.application.use_cases.add_budget_allocation_usecase import (
    AddBudgetAllocationUsecase,
)
from src.spending.budgeting.application.use_cases.remove_budget_allocation_usecase import (
    RemoveBudgetAllocationUsecase,
)
from src.spending.budgeting.application.use_cases.retrieve_budget_overview_usecase import (
    GetBudgetOverviewUsecase,
)
from src.spending.budgeting.application.use_cases.delete_budget_usecase import (
    DeleteBudgetUsecase,
)
from src.spending.budgeting.application.use_cases.update_budget_usecase import (
    UpdateBudgetUsecase,
)

router = APIRouter(
    prefix="/budgets",
    tags=["Budgeting"],
)

BudgetUrlParams = Annotated[UrlParams, Depends()]


@router.post("", status_code=status.HTTP_201_CREATED)
async def create_budget(
    budget_data: BudgetWriteModel,
    auth: AuthDeps,
    budget_service: Annotated[CreateBudgetUseCase, Depends()],
):
    result = await budget_service.execute(
        {"user_id": auth.user_id, "budget_data": budget_data}
    )

    if is_fail(result):
        raise result.value

    return {
        "id": result.value.value,
    }


@router.put(
    "/{aggregate_id}", response_model=BudgetReadModel, status_code=status.HTTP_200_OK
)
async def update_budget(
    aggregate_id: str,
    budget_data: BudgetUpdateModel,
    auth: AuthDeps,
    budget_service: Annotated[UpdateBudgetUsecase, Depends()],
):
    result = await budget_service.execute(aggregate_id, auth.user_id, budget_data)

    if is_fail(result):
        raise result.value

    return {
        "message": "Budget updated successfully",
        "data": BudgetReadModel.from_entity(result.value),
    }


@router.put(
    "/{aggregate_id}/allocate",
    response_model=BudgetReadModel,
    status_code=status.HTTP_200_OK,
)
async def add_budget_allocation(
    aggregate_id: str,
    budget_data: BudgetAllocationWriteModel,
    auth: AuthDeps,
    use_case: Annotated[AddBudgetAllocationUsecase, Depends()],
):
    result = await use_case.execute(aggregate_id, auth.user_id, budget_data)

    if is_fail(result):
        raise result.value

    return {
        "message": "allocation created successfully",
        "data": BudgetReadModel.from_entity(result.value),
    }


@router.get("", response_model=List[BudgetReadModel], status_code=status.HTTP_200_OK)
async def retrieve_all_budgets(
    params: BudgetUrlParams,
    auth: Annotated[AuthDeps, Depends()],
    use_case: Annotated[GetBudgetsUsecase, Depends()],
):
    result = await use_case.execute(auth.user_id)

    if is_fail(result):
        raise result.value

    return result.value


@router.get(
    "/overview",
    response_model=BudgetOverviewReadModel,
    status_code=status.HTTP_200_OK,
)
async def retrieve_budget_overview(
    params: BudgetUrlParams,
    auth: Annotated[AuthDeps, Depends()],
    use_case: Annotated[GetBudgetOverviewUsecase, Depends()],
):
    result = await use_case.execute(auth.user_id, params.page_size)

    if is_fail(result):
        raise result.value

    return result.value


@router.get(
    "/{aggregate_id}",
    response_model=BudgetReadModel,
    status_code=status.HTTP_200_OK,
)
async def retrieve_budget(
    aggregate_id: str,
    auth: Annotated[AuthDeps, Depends()],
    use_case: Annotated[GetBudgetUsecase, Depends()],
):
    result = await use_case.execute(aggregate_id, auth.user_id)

    if is_fail(result):
        raise result.value

    return result.value


@router.delete(
    "/{aggregate_id}",
    status_code=status.HTTP_204_NO_CONTENT,
)
async def delete_all_expense_by_category(
    aggregate_id: str,
    auth: AuthDeps,
    use_case: Annotated[DeleteBudgetUsecase, Depends()],
):
    result = await use_case.execute(aggregate_id, auth.user_id)

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
    use_case: Annotated[RemoveBudgetAllocationUsecase, Depends()],
):
    result = await use_case.execute(aggregate_id, allocation_id, auth.user_id)

    if is_fail(result):
        raise result.value

    return None
