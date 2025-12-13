from typing import Optional

from app.modules.education.blogs.models.blog import BlogBase


class CreateBlog(BlogBase):
    slug: Optional[str] = None
