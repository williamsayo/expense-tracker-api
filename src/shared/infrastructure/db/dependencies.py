from .base import AsyncSessionLocal, engine, Base
from sqlalchemy.ext.asyncio import AsyncSession
from typing import AsyncGenerator

async def init_db():
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

async def get_session() -> AsyncGenerator[AsyncSession]:
    async with AsyncSessionLocal() as session:
        yield session