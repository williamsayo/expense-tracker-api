from fastapi import FastAPI, APIRouter
from src.core.config import settings
from src.shared.loggers.logging import setup_logging, LogLevel
from src.shared.infrastructure.db.base import engine, AsyncSessionLocal
from src.shared.infrastructure.db.dependencies import init_db
from src.shared.infrastructure.dispatcher.dependencies import register_handler
from src.shared.domain.types.event_types import EventTypes
from src.core.exception_handler import register_errors
from src.core.middlewares import register_middlewares
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
    register_handler(EventTypes.EXPENSE_CREATED, OnExpenseCreated(AsyncSessionLocal))
    register_handler(EventTypes.BUDGET_CREATED, OnBudgetCreated(AsyncSessionLocal))
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
app.include_router(identity_router, prefix="/api/v1")
app.include_router(expense_router, prefix="/api/v1")
app.include_router(budget_router, prefix="/api/v1")
