from aiodynamo.credentials import StaticCredentials, Key
from aiodynamo.client import Client
from aiohttp import ClientSession
from aiodynamo.http.aiohttp import AIOHTTP
from src.spending.budgeting.infrastructure.repositories.dynamodb.budget_repo import (
    BudgetRepository,
)
from src.spending.expenses.infrastructure.repositories.dynamodb.expense_repo import (
    ExpenseRepository,
)
from src.identity.infrastructure.repositories.dynamodb.user_repo import UserRepository
from .base import AsyncSessionLocal, engine, Base
from src.core.config import settings
from sqlalchemy.ext.asyncio import AsyncSession
from typing import AsyncGenerator


async def init_db():
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)


async def get_session() -> AsyncGenerator[AsyncSession]:
    async with AsyncSessionLocal() as session:
        yield session


def get_dynamodb_client(session: ClientSession) -> Client:
    """Returns the context manager — use this anywhere."""
    return Client(
        http=AIOHTTP(session),
        credentials=StaticCredentials(
            Key(
                id=settings.aws_access_key_id,
                secret=settings.aws_secret_access_key,
            )
        ),
        region=settings.aws_region_name,
    )


async def init_dynamodb():
    async with ClientSession() as session:
        client = get_dynamodb_client(session)
        await UserRepository.create_table("user", client)
        await ExpenseRepository.create_table("expense", client)
        await BudgetRepository.create_table("budget", client)


async def get_dynamodb() -> AsyncGenerator:
    async with ClientSession() as session:
        client = get_dynamodb_client(session)
        yield client
