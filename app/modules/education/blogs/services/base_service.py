from typing import Optional

from sqlalchemy.orm.strategy_options import selectinload
from sqlmodel import Session, func, select

from app.modules.common.services.s3_service import S3Service
from app.modules.education.blogs.schema.blogs import BlogResponse

from ..models.blog import Blog, BlogStatus


class BaseBlogService:
    def __init__(self):
        self.s3_service = S3Service()

    def get_blog_instance(
        self,
        session: Session,
        blog_id: Optional[int] = None,
        blog_slug: Optional[str] = None,
        status: Optional[BlogStatus] = None,
        load_categories: Optional[bool] = False,
        load_metadata: Optional[bool] = False,
    ):
        blog: Blog | None = None

        statement = select(Blog)

        if blog_id:
            statement = statement.where(Blog.id == blog_id)
        elif blog_slug:
            statement = statement.where(Blog.slug == blog_slug)
        else:
            raise ValueError("Blog ID or Blog Slug is required")

        if status:
            statement = statement.where(Blog.status == status)

        if load_categories:
            statement = statement.options(selectinload(Blog.categories))

        if load_metadata:
            statement = statement.options(selectinload(Blog.meta_data))

        blog = session.exec(statement).one_or_none()

        return blog

    def get_blog_with_details(
        self,
        session: Session,
        blog_slug: Optional[str] = None,
        blog_id: Optional[int] = None,
        status: Optional[BlogStatus] = None,
    ):
        blog = self.get_blog_instance(
            session=session,
            blog_slug=blog_slug,
            blog_id=blog_id,
            status=status,
            load_categories=True,
            load_metadata=True,
        )

        if not blog:
            return None

        blog_dict = blog.model_dump()
        blog_dict["categories"] = blog.categories

        if blog.thumbnail_id:
            thumbnail = self.s3_service.get_file(object_name=blog.thumbnail_id)
            if thumbnail:
                blog_dict["thumbnail"] = thumbnail
        return BlogResponse(**blog_dict)

    def get_blogs(
        self,
        session: Session,
        page: int,
        limit: int,
        status: Optional[BlogStatus] = None,
        search: Optional[str] = None,
    ):
        statement = select(Blog)

        if status:
            statement = statement.where(Blog.status == status)

        if search:
            statement = statement.where(Blog.title.contains(f"%{search}%"))

        total_items = session.exec(select(func.count()).select_from(statement.subquery())).one()

        blogs = session.exec(
            statement.order_by(Blog.updated_at.desc()).offset((page - 1) * limit).limit(limit)
        ).all()

        blogs_data = []
        for blog in blogs:
            blog_dict = blog.model_dump()
            if blog.thumbnail_id:
                thumbnail = self.s3_service.get_file(object_name=blog.thumbnail_id)
                if thumbnail:
                    blog_dict["thumbnail"] = thumbnail

            blog_dict = BlogResponse(**blog_dict)
            blogs_data.append(blog_dict)

        return blogs_data, total_items
