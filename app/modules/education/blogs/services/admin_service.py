from uuid import uuid4

from slugify import slugify
from sqlmodel import select
from sqlmodel.ext.asyncio.session import AsyncSession

from app.modules.education.blogs.schema.blogs import CreateBlog, UpdateBlog
from app.modules.education.shared.model import EducationCategory

from ..models.blog import Blog
from .base_service import BaseBlogService


class AdminBlogService(BaseBlogService):
    async def create_blog(self, session: AsyncSession, blog_data: CreateBlog):
        if not blog_data.slug:
            base_slug = slugify(blog_data.title)
            unique_suffix = str(uuid4().hex)[:6]
            blog_data.slug = f"{base_slug}-{unique_suffix}"

        blog = await self.get_blog_instance(session=session, blog_slug=blog_data.slug)

        if blog:
            return None

        result = await session.exec(
            select(EducationCategory).where(EducationCategory.id.in_(blog_data.categories))
        )
        categories = result.all()

        blog_dict = blog_data.model_dump(exclude={"categories"})

        blog = Blog(**blog_dict)
        blog.categories = categories

        try:
            session.add(blog)
            await session.commit()
            await session.refresh(blog)
            return blog
        except Exception as e:
            await session.rollback()
            raise e

    async def update_blog(self, session: AsyncSession, blog_slug: str, blog_data: UpdateBlog):
        blog = await self.get_blog_instance(session=session, blog_slug=blog_slug)

        if not blog:
            return None

        blog_dict = blog_data.model_dump(exclude_unset=True, exclude={"slug", "categories"})

        try:
            if blog_data.categories is not None:
                result = await session.exec(
                    select(EducationCategory).where(EducationCategory.id.in_(blog_data.categories))
                )
                categories = result.all()
                blog.categories.clear()
                blog.categories.extend(categories)

            blog.sqlmodel_update(blog_dict)
            session.add(blog)
            await session.commit()
            await session.refresh(blog)
            return blog
        except Exception as e:
            await session.rollback()
            raise e
