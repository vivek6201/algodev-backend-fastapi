from sqlmodel import Session, create_engine
from sqlalchemy.orm import sessionmaker
from typing import Generator
from app.config.settings import settings
import logging

logger = logging.getLogger(__name__)

# Create database engine
engine = create_engine(
    settings.DATABASE_URL,
    echo=settings.DEBUG,  # Log SQL queries in debug mode
    pool_pre_ping=True,  # Verify connections before using them
    pool_size=5,  # Number of connections to maintain
    max_overflow=10,  # Maximum number of connections beyond pool_size
)

# Create session factory
SessionLocal = sessionmaker(
    autocommit=False,
    autoflush=False,
    bind=engine,
    class_=Session
)

def get_session() -> Generator[Session, None, None]:
    """
    Dependency for getting database session.
    Use with FastAPI Depends for database operations.
    """
    
    session = SessionLocal()
    try:
        yield session
        session.commit()  # Commit if no exception
    except Exception:
        session.rollback()  # Rollback on exception
        raise
    finally:
        session.close()