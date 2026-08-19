"""
1. Configures the Async SQLAlchemy engine using aiosqlite for non-blocking I/O.
2. Provides the async session factory and dependency injection for FastAPI routes.
3. Initializes database tables from declarative base models.
"""

import logging
from typing import AsyncGenerator
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine, async_sessionmaker

# We import Base from our models to ensure all tables are registered
from backend.app.models.campaign import Base
import backend.app.models.post  # noqa: F401 (Registers the Post table)

logger = logging.getLogger(__name__)

# Using SQLite for local development. In production, swap with asyncpg (PostgreSQL)
# e.g. postgresql+asyncpg://user:pass@localhost/social_db
DATABASE_URL = "sqlite+aiosqlite:///./social_manager.db"

# Create the async engine
engine = create_async_engine(
    DATABASE_URL,
    echo=False,  # Set to True to see raw SQL logs
    future=True,
    connect_args={"check_same_thread": False} # Required for SQLite
)

# Async Session Factory
AsyncSessionLocal = async_sessionmaker(
    bind=engine,
    class_=AsyncSession,
    expire_on_commit=False,
    autoflush=False
)


async def init_db() -> None:
    """
    Creates all tables in the database if they don't exist.
    """
    logger.info("🛠️ Initializing Async Database Engine...")
    async with engine.begin() as conn:
        # Create all tables (campaigns, posts)
        await conn.run_sync(Base.metadata.create_all)
    logger.info("✅ Database tables verified/created successfully.")


async def get_db() -> AsyncGenerator[AsyncSession, None]:
    """
    Dependency injection for FastAPI or manual context management.
    Yields a safe async database session and automatically closes it.
    """
    async with AsyncSessionLocal() as session:
        try:
            yield session
        finally:
            await session.close()
