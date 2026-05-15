from fastapi import FastAPI, APIRouter
from src.core.config import settings
from src.shared.loggers.logging import setup_logging, LogLevel
from src.shared.infrastructure.db.dependencies import init_dynamodb
from src.core.exception_handler import register_errors
from src.core.middlewares import register_middlewares
from contextlib import asynccontextmanager
from src.identity.presentation.web.v1.route import router as identity_router
from src.spending.expenses.presentation.web.v1.route import router as expense_router
from src.spending.budgeting.presentation.web.v1.route import router as budget_router


@asynccontextmanager
async def lifespan(_app: FastAPI):
    setup_logging(LogLevel.INFO)
    await init_dynamodb()
    yield


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
