from datetime import datetime
from enum import Enum
from typing import List, Optional

from sqlmodel import Field, Relationship, SQLModel

from app.common.db.utils import pg_enum
from app.modules.education.shared.model import BlogCategoryLink


class BlogStatus(Enum):
    """Enum for blog status"""

    DRAFT = "DRAFT"
    PUBLISHED = "PUBLISHED"


class BlogBase(SQLModel):
    title: str
    slug: str = Field(index=True, unique=True)
    description: str
    content: str
    thumbnail_id: Optional[str] = None
    status: BlogStatus = pg_enum(BlogStatus, default=BlogStatus.DRAFT, nullable=False)


class Blog(BlogBase, table=True):
    id: Optional[int] = Field(default=None, primary_key=True, index=True)

    categories: List["EducationCategory"] = Relationship(  # noqa: F821
        back_populates="blogs", link_model=BlogCategoryLink
    )

    created_at: datetime = Field(default_factory=datetime.now)
    updated_at: datetime = Field(
        default_factory=datetime.now, sa_column_kwargs={"onupdate": datetime.now}
    )
