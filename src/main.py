from fastapi import FastAPI, APIRouter
from src.core.config import get_settings
from src.shared.infrastructure.services.aws.config import get_aioboto3_session
from src.shared.loggers.logging import setup_logging, LogLevel
from src.shared.infrastructure.db.base import engine
from src.shared.infrastructure.db.dependencies import init_db
from src.shared.application.events.dispatcher.dependencies import (
    register_handler,
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
    await init_db()
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
async def health_check():
    return {"status": "ok"}


app.include_router(router)
register_routers(
    app,
    routers=[identity_router, dashboard_router, expense_router, budget_router],
    version="v1",
)
