from datetime import datetime
from typing import List, Optional

from sqlmodel import Column, Field, ForeignKey, Relationship, SQLModel


class CategoriesBase(SQLModel):
    name: str


class BlogCategoryLink(SQLModel, table=True):
    """Composite Primary Key (Both keys together are unique)"""

    blog_id: Optional[int] = Field(default=None, foreign_key="blog.id", primary_key=True)
    category_id: Optional[int] = Field(
        default=None,
        sa_column=Column(ForeignKey("educationcategory.id", ondelete="CASCADE"), primary_key=True),
    )


class EducationCategory(CategoriesBase, table=True):
    id: Optional[int] = Field(default=None, primary_key=True, index=True)

    blogs: List["Blog"] = Relationship(back_populates="categories", link_model=BlogCategoryLink)  # noqa: F821

    created_at: datetime = Field(default_factory=datetime.now)
    updated_at: datetime = Field(
        default_factory=datetime.now, sa_column_kwargs={"onupdate": datetime.now}
    )
