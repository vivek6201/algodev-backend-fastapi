import math
from typing import Optional

from sqlalchemy.orm.strategy_options import selectinload
from sqlmodel import func, select
from sqlmodel.ext.asyncio.session import AsyncSession

from app.common.cache.decorators import cached, invalidate_cache
from app.common.lib.formatter import ListResponse
from app.modules.common.services.s3_service import S3Service
from app.modules.education.blogs.schema.blogs import BlogResponse
from app.modules.education.shared.model import ReactionType
from app.modules.education.shared.services.reaction_service import ReactionService

from ..models.blog import Blog, BlogStatus


class BaseBlogService:
    def __init__(self):
        self.s3_service = S3Service()
        self.reaction_service = ReactionService()

    async def get_blog_instance(
        self,
        session: AsyncSession,
        blog_id: Optional[int] = None,
        blog_slug: Optional[str] = None,
        status: Optional[BlogStatus] = None,
        load_categories: Optional[bool] = False,
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

        result = await session.exec(statement)
        blog = result.one_or_none()

        return blog

    @cached(
        key_prefix="blogs", tags=["blog_{blog_id}", "blog_{blog_slug}"], response_model=BlogResponse
    )
    async def get_blog_with_details(
        self,
        session: AsyncSession,
        blog_slug: Optional[str] = None,
        blog_id: Optional[int] = None,
        status: Optional[BlogStatus] = None,
    ):
        blog = await self.get_blog_instance(
            session=session,
            blog_slug=blog_slug,
            blog_id=blog_id,
            status=status,
            load_categories=True,
        )

        if not blog:
            return None

        blog_dict = blog.model_dump()
        blog_dict["categories"] = blog.categories

        if blog.thumbnail_id:
            thumbnail = await self.s3_service.get_file(object_name=blog.thumbnail_id)
            if thumbnail:
                blog_dict["thumbnail"] = thumbnail
        return BlogResponse(**blog_dict)

    @cached(key_prefix="blogs", tags=["blogs_list"], response_model=ListResponse[BlogResponse])
    async def get_blogs(
        self,
        session: AsyncSession,
        page: int,
        limit: int,
        status: Optional[BlogStatus] = None,
        search: Optional[str] = None,
    ) -> ListResponse[BlogResponse]:
        statement = select(Blog)

        if status:
            statement = statement.where(Blog.status == status)

        if search:
            statement = statement.where(Blog.title.contains(f"%{search}%"))

        count_result = await session.exec(select(func.count()).select_from(statement.subquery()))
        total_items = count_result.one()

        result = await session.exec(
            statement.order_by(Blog.updated_at.desc()).offset((page - 1) * limit).limit(limit)
        )
        blogs = result.all()

        blogs_data = []
        for blog in blogs:
            blog_dict = blog.model_dump()
            if blog.thumbnail_id:
                thumbnail = await self.s3_service.get_file(object_name=blog.thumbnail_id)
                if thumbnail:
                    blog_dict["thumbnail"] = thumbnail

            blog_dict = BlogResponse(**blog_dict)
            blogs_data.append(blog_dict)

        return ListResponse[BlogResponse](
            data=blogs_data,
            total_items=total_items,
            total_pages=math.ceil(total_items / limit) if limit > 0 else 1,
        )

    @cached(key_prefix="blogs", tags=["blog_metadata_{blog_slug}"], response_model=dict)
    async def get_blog_metadata(self, session: AsyncSession, blog_slug: str, user_id: int = None):
        try:
            user_reaction = None
            if user_id:
                user_reaction = await self.reaction_service.get_user_reaction(
                    session=session, content_slug=blog_slug, user_id=user_id
                )

            reaction_counts = await self.reaction_service.get_reaction_counts(
                session=session, content_slug=blog_slug
            )

            return {
                "current_reaction": user_reaction.reaction,
                "likes": reaction_counts["likes"],
                "dislikes": reaction_counts["dislikes"],
            }
        except Exception as e:
            raise e

    @invalidate_cache(tags=["blog_metadata_{blog_slug}"])
    async def toggle_blog_reaction(
        self,
        session: AsyncSession,
        blog_slug: str,
        user_id: int,
        action: str,
    ) -> Optional[dict]:
        """Toggle a reaction on a blog"""
        blog = await self.get_blog_instance(session=session, blog_slug=blog_slug)

        if not blog:
            return None

        # Map action to ReactionType
        reaction_type = ReactionType.LIKE if action == "like" else ReactionType.DISLIKE

        # Toggle reaction using content_slug
        result = await self.reaction_service.toggle_reaction(
            session=session,
            user_id=user_id,
            content_slug=blog.slug,
            reaction_type=reaction_type,
        )

        # Get fresh counts from UserReaction table
        counts = await self.reaction_service.get_reaction_counts(
            session=session,
            content_slug=blog.slug,
        )

        return {
            **result,
            "likes": counts["likes"],
            "dislikes": counts["dislikes"],
        }
