from fastapi import FastAPI, APIRouter
from src.core.config import get_settings, settings
from src.shared.infrastructure.services.aws.config import get_aioboto3_session
from src.shared.infrastructure.services.aws.dependencies import get_s3_client
from src.shared.infrastructure.services.aws.utils import (
    create_bucket,
    set_bucket_policy,
    set_public_access,
    PUBLIC_READ_POLICY,
)
from src.shared.loggers.logging import setup_logging, LogLevel
from src.shared.infrastructure.db.base import engine, AsyncSessionLocal
from src.shared.infrastructure.db.dependencies import init_db
from src.shared.infrastructure.dispatcher.dependencies import register_handler
from src.shared.domain.types.event_types import EventTypes
from src.core.exception_handler import register_errors
from src.core.middlewares import register_middlewares
from src.core.router import register_routers
from contextlib import asynccontextmanager
from src.identity.presentation.web.v1.route import router as identity_router
from src.spending.expenses.presentation.web.v1.route import router as expense_router
from src.spending.budgeting.presentation.web.v1.route import router as budget_router
from src.spending.budgeting.application.services.event_handler import (
    OnExpenseCreated,
    OnBudgetCreated,
)


@asynccontextmanager
async def lifespan(_app: FastAPI):
    await init_db()
    setup_logging(LogLevel.INFO)
    get_settings()
    # Initialize AWS S3 bucket
    async with get_aioboto3_session().client("s3") as s3_client:
        await create_bucket(settings.aws_s3_bucket_name, s3_client)
        await set_public_access(s3_client, settings.aws_s3_bucket_name)
        await set_bucket_policy(
            s3_client, settings.aws_s3_bucket_name, PUBLIC_READ_POLICY
        )

    # register_handler(EventTypes.EXPENSE_CREATED, OnExpenseCreated(AsyncSessionLocal))
    # register_handler(EventTypes.BUDGET_CREATED, OnBudgetCreated(AsyncSessionLocal))
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
    app, routers=[identity_router, expense_router, budget_router], version="v1"
)