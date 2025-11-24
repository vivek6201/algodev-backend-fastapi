from datetime import datetime
from enum import Enum
from typing import List, Optional

from sqlmodel import Column, DateTime, Field, Relationship, SQLModel, func

from app.common.db.utils import pg_enum


class Role(str, Enum):
    """User role enumeration"""

    ADMIN = "ADMIN"
    USER = "USER"
    MODERATOR = "MODERATOR"
    GUEST = "GUEST"
    RECRUITER = "RECRUITER"


class Users(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True, index=True)
    first_name: str
    last_name: str
    email: str = Field(index=True, unique=True)
    username: str = Field(index=True, unique=True)
    password: str
    role: Role = pg_enum(Role, default=Role.USER, nullable=False)

    refresh_token: Optional[str] = Field(default=None, index=True)

    # Email verification
    email_verified: bool = Field(default=False)
    verification_token: Optional[str] = Field(default=None)
    verification_token_expires: Optional[datetime] = Field(default=None)

    # Relationships
    posted_jobs: List["Job"] = Relationship(back_populates="owner")  # noqa: F821
    applications: List["JobApplication"] = Relationship(back_populates="candidate")  # noqa: F821

    # timestamp fields
    created_at: datetime = Field(
        sa_column=Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    )
    updated_at: datetime = Field(
        sa_column=Column(
            DateTime(timezone=True), onupdate=func.now(), server_default=func.now(), nullable=False
        )
    )
