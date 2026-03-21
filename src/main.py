from fastapi import FastAPI
from core.config import settings
from shared.loggers.logging import setup_logging, LogLevel
from shared.infrastructure.db.base import engine
from shared.infrastructure.db.dependencies import init_db
from core.exception_handler import register_errors
from core.middlewares import register_middlewares
from contextlib import asynccontextmanager
from identity.presentation.web.v1.route import router
from expenses.presentation.web.v1.route import router as expense_router
from budgeting.presentation.web.v1.route import router as budget_router

@asynccontextmanager
async def lifespan(_app: FastAPI):
    await init_db()
    setup_logging(LogLevel.INFO)
    yield
    await engine.dispose()


app = FastAPI(
    lifespan=lifespan,
    title=settings.app_name,
    debug=settings.debug,
    version=settings.version,
)

register_errors(app=app)
register_middlewares(app=app)

app.include_router(router, prefix="/api/v1")
app.include_router(expense_router, prefix="/api/v1")
app.include_router(budget_router, prefix="/api/v1")
