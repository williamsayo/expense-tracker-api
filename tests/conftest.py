from pathlib import Path
import os
import sys
from fastapi.testclient import TestClient
import pytest
from sqlalchemy import StaticPool
from src.main import app
from src.shared.infrastructure.db.dependencies import get_session
from src.shared.infrastructure.db.base import Base
from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker, AsyncSession

ROOT = Path(__file__).resolve().parent.parent
SRC = ROOT / "src"

os.environ.setdefault("db_name", "test_db")
os.environ.setdefault("db_password", "test_password")
os.environ.setdefault("db_user", "test_user")
os.environ.setdefault("db_url", "sqlite+aiosqlite:///./test.db")
os.environ.setdefault("redis_host", "localhost")
os.environ.setdefault("redis_port", "6379")
os.environ.setdefault("redis_url", "redis://localhost:6379")
os.environ.setdefault("secret_key", "test-secret-key")
os.environ.setdefault("better_stack_api_token", "test-token")

if str(SRC) not in sys.path:
    sys.path.insert(0, str(SRC))

test_db_url = "sqlite+aiosqlite:///:memory:"

test_engine = create_async_engine(
    test_db_url,
    echo=False,
    connect_args={"check_same_thread": False},
    poolclass=StaticPool,
)

test_async_session = async_sessionmaker(
    bind=test_engine,
    class_=AsyncSession,
    expire_on_commit=False,
    autoflush=False,
    autocommit=False,
)


async def override_get_session():
    async with test_async_session() as session:
        yield session
        await session.rollback()
        await session.close()


app.dependency_overrides[get_session] = override_get_session


@pytest.fixture(scope="session")
def client():
    with TestClient(app) as client:
        yield client


@pytest.fixture(scope="session")
async def init_db():
    async with test_engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
        yield
        await conn.run_sync(Base.metadata.drop_all)
        await conn.close()

    await test_engine.dispose()
