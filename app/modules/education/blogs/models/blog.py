from datetime import datetime
from typing import List, Optional

from sqlmodel import Field, Relationship, SQLModel

from ...model import BlogCategoryLink


class BlogMetadata(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True, index=True)
    blog_id: int = Field(foreign_key="blog.id")
    blog: Optional["Blog"] = Relationship(back_populates="meta_data")

    likes: int = Field(default=0)
    dislikes: int = Field(default=0)


class BlogBase(SQLModel):
    title: str
    slug: str = Field(index=True, unique=True)
    description: str
    content: str
    thumbnail_id: Optional[str] = None


class Blog(BlogBase, table=True):
    id: Optional[int] = Field(default=None, primary_key=True, index=True)

    meta_data: Optional["BlogMetadata"] = Relationship(back_populates="blog")
    categories: List["EducationCategory"] = Relationship(  # noqa: F821
        back_populates="blogs", link_model=BlogCategoryLink
    )

    created_at: datetime = Field(default_factory=datetime.now)
    updated_at: datetime = Field(
        default_factory=datetime.now, sa_column_kwargs={"onupdate": datetime.now}
    )
