from datetime import datetime
from enum import Enum
from typing import List, Optional

from sqlmodel import Column, DateTime, Field, Relationship, SQLModel, func

from app.common.db.utils import pg_enum
from app.modules.auth.models.session import Session


class Role(str, Enum):
    """User role enumeration"""

    CANDIDATE = "CANDIDATE"
    RECRUITER = "RECRUITER"


class Users(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True, index=True)
    first_name: str
    last_name: str
    email: str = Field(index=True, unique=True)
    username: str = Field(index=True, unique=True)
    password: str
    role: Role = pg_enum(Role, default=Role.CANDIDATE, nullable=False)

    # Email verification
    email_verified: bool = Field(default=False)
    verification_token: Optional[str] = Field(default=None)
    verification_token_expires: Optional[datetime] = Field(default=None)

    # Session Configuration
    max_sessions: int = Field(default=2)

    # Relationships
    posted_jobs: List["Job"] = Relationship(back_populates="owner")  # noqa: F821
    applications: List["JobApplication"] = Relationship(back_populates="candidate")  # noqa: F821
    sessions: List["Session"] = Relationship(
        back_populates="user", sa_relationship_kwargs={"cascade": "all, delete-orphan"}
    )

    # timestamp fields
    created_at: datetime = Field(
        sa_column=Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    )
    updated_at: datetime = Field(
        sa_column=Column(
            DateTime(timezone=True), onupdate=func.now(), server_default=func.now(), nullable=False
        )
    )
