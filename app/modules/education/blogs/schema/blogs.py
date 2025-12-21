from datetime import datetime
from typing import List, Optional

from pydantic import Field
from pydantic.main import BaseModel

from app.common.lib.formatter import FileResponse
from app.modules.education.blogs.models.blog import BlogBase, BlogStatus
from app.modules.education.shared.model import EducationCategory


class CreateBlog(BlogBase):
    slug: Optional[str] = None
    categories: List[int]
    status: Optional[BlogStatus] = None


class UpdateBlog(BlogBase):
    title: Optional[str] = None
    description: Optional[str] = None
    content: Optional[str] = None
    categories: Optional[List[int]] = None
    status: Optional[BlogStatus] = None
    slug: Optional[str] = None


class BlogResponse(BlogBase):
    id: int
    categories: Optional[List[EducationCategory]] = None
    thumbnail: Optional[FileResponse] = None
    thumbnail_id: Optional[str] = Field(default=None, exclude=True)

    created_at: datetime
    updated_at: datetime


class BlogMetadataResponse(BaseModel):
    likes: int
    dislikes: int
