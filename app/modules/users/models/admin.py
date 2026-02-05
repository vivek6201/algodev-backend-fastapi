from datetime import datetime
from enum import Enum
from typing import List, Optional

from sqlmodel import Column, DateTime, Field, Relationship, SQLModel, func

from app.common.db.utils import pg_enum
from app.modules.auth.models.session import AdminSession


class AdminRole(str, Enum):
    """Admin role enumeration"""

    ADMIN = "ADMIN"
    SUPER_ADMIN = "SUPER_ADMIN"
    MODERATOR = "MODERATOR"


class Admin(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True, index=True)
    first_name: str
    last_name: str
    email: str = Field(index=True, unique=True)
    password: str
    role: AdminRole = pg_enum(AdminRole, default=AdminRole.ADMIN, nullable=False)

    # Relationships
    posted_jobs: List["Job"] = Relationship(back_populates="admin")  # noqa: F821
    sessions: List["AdminSession"] = Relationship(
        back_populates="admin", sa_relationship_kwargs={"cascade": "all, delete-orphan"}
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
