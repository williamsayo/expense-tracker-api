from typing import Annotated
from datetime import date
from fastapi.routing import APIRouter
from fastapi import Depends, Query, status
from result import is_fail
from src.dashboard.application.use_cases.retrieve_overview_usecase import (
    GetOverviewUsecase,
)
from src.dashboard.infrastructure.adapters.dto.dashboard import DashboardReadModel
from src.shared.utils.auth.dependencies import AuthDeps

router = APIRouter(
    prefix="/dashboard",
    tags=["Overview"],
)


@router.get(
    "/overview",
    status_code=status.HTTP_200_OK,
    response_model=DashboardReadModel,
    summary="Get an overview spending data",
    description="Returns an overview of spending data for the dashboard.",
    response_description="An overview of spending data.",
)
async def dashboard_overview(
    usecase: Annotated[GetOverviewUsecase, Depends()],
    authenticated_user: AuthDeps,
    period: date = Query(
        default_factory=date.today,
        description="The period for which to retrieve the overview. Defaults to the current date.",
    ),
):
    result = await usecase.execute(
        {
            "user_id": authenticated_user.user_id,
            "period": period,
        }
    )

    if is_fail(result):
        raise result.value

    return result.value
