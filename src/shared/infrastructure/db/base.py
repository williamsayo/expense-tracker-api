from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker, AsyncSession
from src.core.config import settings
from sqlalchemy.orm import DeclarativeBase


class Base(DeclarativeBase):
    """Base declarative model for ORM entities."""
    ...

engine = create_async_engine(
    settings.db_url,
    connect_args={"check_same_thread": not settings.debug} if "sqlite" in settings.db_url else {},
    # echo=True,
    future=True,
)

AsyncSessionLocal = async_sessionmaker(
    bind=engine, class_=AsyncSession, expire_on_commit=False
)
