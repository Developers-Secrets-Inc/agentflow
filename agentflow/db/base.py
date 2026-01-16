"""Database base configuration and engine setup."""

from typing import AsyncGenerator

from sqlalchemy.ext.asyncio import (
    AsyncEngine,
    AsyncSession,
    async_sessionmaker,
    create_async_engine,
)
from sqlalchemy.orm import DeclarativeBase

from agentflow.config.database import get_database_settings


class Base(DeclarativeBase):
    """Base class for all database models."""

    pass


# Global engine and sessionmaker
_engine: AsyncEngine | None = None
_async_session_maker: async_sessionmaker[AsyncSession] | None = None


def get_engine() -> AsyncEngine:
    """Get the database engine (singleton)."""
    global _engine
    if _engine is None:
        settings = get_database_settings()
        _engine = create_async_engine(
            settings.async_url,
            pool_size=settings.db_pool_size,
            max_overflow=settings.db_max_overflow,
            echo=False,
        )
    return _engine


def get_session_maker() -> async_sessionmaker[AsyncSession]:
    """Get the session maker (singleton)."""
    global _async_session_maker
    if _async_session_maker is None:
        engine = get_engine()
        _async_session_maker = async_sessionmaker(
            engine,
            class_=AsyncSession,
            expire_on_commit=False,
        )
    return _async_session_maker


async def get_db_session() -> AsyncGenerator[AsyncSession, None]:
    """
    Get a database session.

    Yields:
        AsyncSession: Database session
    """
    session_maker = get_session_maker()
    async with session_maker() as session:
        try:
            yield session
        finally:
            await session.close()


async def init_db() -> None:
    """Initialize the database engine."""
    # This will create the engine on first call
    get_engine()


async def close_db() -> None:
    """Close the database engine."""
    global _engine
    if _engine is not None:
        await _engine.dispose()
        _engine = None
        _async_session_maker = None
