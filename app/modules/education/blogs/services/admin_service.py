from uuid import uuid4

from slugify import slugify
from sqlmodel import Session, select

from app.modules.education.blogs.schema.blogs import CreateBlog, UpdateBlog
from app.modules.education.shared.model import EducationCategory

from ..models.blog import Blog
from .base_service import BaseBlogService


class AdminBlogService(BaseBlogService):
    def create_blog(self, session: Session, blog_data: CreateBlog):
        if not blog_data.slug:
            base_slug = slugify(blog_data.title)
            unique_suffix = str(uuid4().hex)[:6]
            blog_data.slug = f"{base_slug}-{unique_suffix}"

        blog = self.get_blog_instance(session=session, blog_slug=blog_data.slug)

        if blog:
            return None

        categories = session.exec(
            select(EducationCategory).where(EducationCategory.id.in_(blog_data.categories))
        ).all()

        blog_dict = blog_data.model_dump(exclude={"categories"})

        blog = Blog(**blog_dict)
        blog.categories = categories

        try:
            session.add(blog)
            session.commit()
            session.refresh(blog)
            return blog
        except Exception as e:
            session.rollback()
            raise e

    def update_blog(self, session: Session, blog_slug: str, blog_data: UpdateBlog):
        blog = self.get_blog_instance(session=session, blog_slug=blog_slug)

        if not blog:
            return None

        blog_dict = blog_data.model_dump(exclude_unset=True, exclude={"slug", "categories"})

        try:
            if blog_data.categories is not None:
                categories = session.exec(
                    select(EducationCategory).where(EducationCategory.id.in_(blog_data.categories))
                ).all()
                blog.categories.clear()
                blog.categories.extend(categories)

            blog.sqlmodel_update(blog_dict)
            session.add(blog)
            session.commit()
            session.refresh(blog)
            return blog
        except Exception as e:
            session.rollback()
            raise e
