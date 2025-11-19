from sqlmodel import SQLModel, Field, Column, DateTime, func, Enum as SQLEnum
from typing import Optional
from datetime import datetime
from sqlmodel import Relationship
from enum import Enum


class Role(str, Enum):
    """User role enumeration"""
    ADMIN = "ADMIN"
    USER = "USER"
    MODERATOR = "MODERATOR"
    GUEST = "GUEST"
    RECRUITER = "RECRUITER"


class User(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True, index=True)
    first_name: str
    last_name: str
    email: str = Field(index=True, unique=True)
    username: str = Field(index=True, unique=True)
    password: str
    role: Role = Field(
        sa_column=Column(SQLEnum(Role), nullable=False, server_default=Role.USER)
    )

    refresh_token: Optional[str] = Field(default=None, index=True)

    created_at: datetime = Field(
        sa_column=Column(DateTime(timezone=True),
                         server_default=func.now(), nullable=False)
    )
    updated_at: datetime = Field(
        sa_column=Column(DateTime(timezone=True), onupdate=func.now(
        ), server_default=func.now(), nullable=False)
    )