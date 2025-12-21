from datetime import datetime
from enum import Enum
from typing import List, Optional

from sqlalchemy import Index, UniqueConstraint
from sqlmodel import Field, Relationship, SQLModel

from app.common.db.utils import pg_enum


class ReactionType(str, Enum):
    """Types of reactions users can give"""

    LIKE = "LIKE"
    DISLIKE = "DISLIKE"


class UserReaction(SQLModel, table=True):
    """Reaction table - tracks user reactions using content_slug (unique identifier)"""

    id: Optional[int] = Field(default=None, primary_key=True)
    user_id: int = Field(foreign_key="users.id", index=True)
    content_slug: str = Field(index=True)  # Unique slug of blog/tutorial/etc
    reaction: ReactionType = pg_enum(ReactionType, nullable=False)
    created_at: datetime = Field(default_factory=datetime.now)

    __table_args__ = (
        # One reaction per user per content
        UniqueConstraint("user_id", "content_slug", name="uq_user_content_reaction"),
        Index("idx_user_content_reaction", "user_id", "content_slug"),
    )


class CategoriesBase(SQLModel):
    name: str


class BlogCategoryLink(SQLModel, table=True):
    """Composite Primary Key (Both keys together are unique)"""

    blog_id: Optional[int] = Field(default=None, foreign_key="blog.id", primary_key=True)
    category_id: Optional[int] = Field(
        default=None,
        foreign_key="educationcategory.id",
        primary_key=True,
        ondelete="CASCADE",
    )


class EducationCategory(CategoriesBase, table=True):
    id: Optional[int] = Field(default=None, primary_key=True, index=True)

    blogs: List["Blog"] = Relationship(back_populates="categories", link_model=BlogCategoryLink)  # noqa: F821

    created_at: datetime = Field(default_factory=datetime.now)
    updated_at: datetime = Field(
        default_factory=datetime.now, sa_column_kwargs={"onupdate": datetime.now}
    )
