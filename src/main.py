from datetime import UTC, datetime
from fastapi import Depends, FastAPI, APIRouter
from boilerplate import ServiceUnavailableError
from sqlalchemy import text
from types_aiobotocore_dynamodb import DynamoDBClient
from src.core.config import get_settings
from src.shared.infrastructure.services.aws.config import get_aioboto3_session
from src.shared.infrastructure.services.aws.dependencies import get_dynamodb_client
from src.shared.loggers.logging import setup_logging, LogLevel
from src.shared.infrastructure.db.base import engine
from src.shared.infrastructure.db.dependencies import get_session, AsyncSession
from src.shared.application.events.dispatcher.dependencies import (
    register_handlers,
)
from src.shared.domain.types.event_types import EventTypes
from src.core.exception_handler import register_errors
from src.core.middlewares import register_middlewares
from src.core.router import register_routers
from contextlib import asynccontextmanager
from src.identity.presentation.web.v1.route import router as identity_router
from src.spending.expenses.presentation.web.v1.route import router as expense_router
from src.spending.budgeting.presentation.web.v1.route import router as budget_router
from src.dashboard.presentation.web.v1.route import router as dashboard_router
from src.dashboard.application.events.event_handler import (
    OnUserCreated,
    OnExpenseCreated,
    OnBudgetCreated,
)

settings = get_settings()

sessions = {}


@asynccontextmanager
async def lifespan(_app: FastAPI):
    setup_logging(LogLevel.INFO)
    async with get_aioboto3_session().resource("dynamodb") as dynamodb_client:
        table = await dynamodb_client.Table(settings.dynamodb_dashboard_table_name)
        sessions["dynamodb"] = dynamodb_client
        register_handlers(
            [
                (EventTypes.BUDGET_CREATED, OnBudgetCreated(dynamodb_client, table)),
                (EventTypes.EXPENSE_CREATED, OnExpenseCreated(dynamodb_client, table)),
                (EventTypes.USER_CREATED, OnUserCreated(dynamodb_client, table)),
            ]
        )
    yield
    await engine.dispose()


app = FastAPI(
    lifespan=lifespan,
    title=settings.app_name,
    debug=settings.debug,
    version=settings.version,
)

router = APIRouter()

register_errors(app=app)
register_middlewares(app=app)


# health check endpoint
@router.get("/healthz", tags=["Health Check"])
async def health_check(
    db: AsyncSession = Depends(get_session),
    dynamodb: DynamoDBClient = Depends(get_dynamodb_client),
):
    try:
        await db.execute(text("SELECT 1"))

    except Exception as error:
        raise ServiceUnavailableError(
            id="database_unavailable",
            message=f"Database unavailable: {error}",
        )

    try:
        await dynamodb.describe_table(TableName=settings.dynamodb_dashboard_table_name)
    except Exception as error:
        raise ServiceUnavailableError(
            id="dynamodb_unavailable",
            message=f"DynamoDB unavailable: {error}",
        )

    return {
        "status": "healthy",
        "database": "connected",
        "dynamodb": "connected",
        "version": settings.version,
        "timestamp": datetime.now(UTC),
    }


app.include_router(router)
register_routers(
    app,
    routers=[identity_router, dashboard_router, expense_router, budget_router],
    version="v1",
)
