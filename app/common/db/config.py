import logging
import ssl
from typing import Generator

from sqlalchemy.ext.asyncio import create_async_engine
from sqlalchemy.orm import sessionmaker
from sqlmodel.ext.asyncio.session import AsyncSession

from app.config.settings import settings

logger = logging.getLogger(__name__)

# Create database engine
engine = create_async_engine(
    settings.ASYNC_DATABASE_URL,
    echo=settings.DEBUG,  # Log SQL queries in debug mode
    pool_pre_ping=True,  # Verify connections before using them
    pool_size=5,  # Number of connections to maintain
    max_overflow=10,  # Maximum number of connections beyond pool_size
    connect_args={"ssl": ssl.create_default_context()},
)

# Create session factory
SessionLocal = sessionmaker(
    autocommit=False, autoflush=False, bind=engine, class_=AsyncSession, expire_on_commit=False
)


async def get_session() -> Generator[AsyncSession, None, None]:
    """
    Dependency for getting database session.
    Use with FastAPI Depends for database operations.
    """

    async with SessionLocal() as session:
        try:
            yield session
            await session.commit()  # Commit if no exception
        except Exception:
            await session.rollback()  # Rollback on exception
            raise
        finally:
            await session.close()
