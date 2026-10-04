"""
Database connection and session management.

Per project rules:
- Use database transactions for multi-step operations
- Roll back on failure
- Use foreign keys, unique constraints, indexes
"""

from sqlalchemy.ext.asyncio import (
    AsyncSession,
    async_sessionmaker,
    create_async_engine,
)
from sqlalchemy.orm import DeclarativeBase

from app.config import settings

engine = create_async_engine(
    settings.database_url,
    echo=settings.python_env == "development",
)

async_session_factory = async_sessionmaker(
    engine,
    class_=AsyncSession,
    expire_on_commit=False,
)

# Alias for worker.py
AsyncSessionLocal = async_session_factory


class Base(DeclarativeBase):
    """Base class for all SQLAlchemy ORM models."""

    pass


async def get_db() -> AsyncSession:  # type: ignore[misc]
    """
    Dependency that yields a database session.

    Usage in route handlers:
        async def my_route(db: AsyncSession = Depends(get_db)):
            ...

    The session is automatically committed on success
    and rolled back on exception.
    """
    async with async_session_factory() as session:
        try:
            yield session
            await session.commit()
        except Exception:
            await session.rollback()
            raise
