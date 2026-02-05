import uuid
from datetime import datetime
from typing import Optional

from sqlmodel import Column, DateTime, Field, Relationship, SQLModel, func


class BaseSession(SQLModel):
    id: uuid.UUID = Field(default_factory=uuid.uuid4, primary_key=True, index=True)
    refresh_token: str = Field(index=True, unique=True)
    user_agent: Optional[str] = Field(default=None)
    ip_address: Optional[str] = Field(default=None)


class Session(BaseSession, table=True):
    user_id: int = Field(foreign_key="users.id", index=True)

    expires_at: datetime = Field(sa_column=Column(DateTime(timezone=True), nullable=False))

    created_at: datetime = Field(
        sa_column=Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    )
    last_active_at: datetime = Field(
        sa_column=Column(
            DateTime(timezone=True), server_default=func.now(), onupdate=func.now(), nullable=False
        )
    )

    # Relationships
    user: "Users" = Relationship(back_populates="sessions")


class AdminSession(BaseSession, table=True):
    __tablename__ = "admin_sessions"
    admin_id: int = Field(foreign_key="admin.id", index=True)

    expires_at: datetime = Field(sa_column=Column(DateTime(timezone=True), nullable=False))

    created_at: datetime = Field(
        sa_column=Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    )
    last_active_at: datetime = Field(
        sa_column=Column(
            DateTime(timezone=True), server_default=func.now(), onupdate=func.now(), nullable=False
        )
    )

    # Relationships
    admin: "Admin" = Relationship(back_populates="sessions")
