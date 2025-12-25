from typing import Optional

from sqlmodel.ext.asyncio.session import AsyncSession
from starlette.status import HTTP_404_NOT_FOUND

from app.common.lib.formatter import ErrorResponse, SuccessResponse
from app.modules.education.blogs.models.blog import BlogStatus

from ..services.base_service import BaseBlogService


class BaseBlogController:
    def __init__(self):
        self.base_service = BaseBlogService()

    async def get_blogs(self, session: AsyncSession, params: Optional[dict] = None):
        try:
            blogs, total_items = await self.base_service.get_blogs(session=session, **params)

            data = {
                "data": blogs,
                "page": params.get("page", 1),
                "limit": params.get("limit", 10),
                "total_items": total_items,
            }

            return SuccessResponse(message="Blogs fetched successfully", data=data)

        except Exception as e:
            print(e)
            return ErrorResponse(message="Something went wrong", error=str(e))

    async def get_blog(self, session: AsyncSession, blog_slug: str):
        try:
            blog = await self.base_service.get_blog_with_details(
                session=session, blog_slug=blog_slug, status=BlogStatus.PUBLISHED
            )

            if not blog:
                return ErrorResponse(message="Blog not found", status_code=HTTP_404_NOT_FOUND)

            return SuccessResponse(message="Blog fetched successfully", data=blog)
        except Exception as e:
            print(e)
            return ErrorResponse(message="Something went wrong", error=str(e))

    async def get_blog_metadata(
        self, session: AsyncSession, blog_slug: str, user_id: Optional[int] = None
    ):
        try:
            blog = await self.base_service.get_blog_metadata(
                session=session, blog_slug=blog_slug, user_id=user_id
            )

            if not blog:
                return ErrorResponse(message="Blog not found", status_code=HTTP_404_NOT_FOUND)

            return SuccessResponse(message="Blog metadata fetched successfully", data=blog)
        except Exception as e:
            print(e)
            return ErrorResponse(message="Something went wrong", error=str(e))

    async def update_blog_reaction(
        self, session: AsyncSession, blog_slug: str, user_id: int, action: str
    ):
        try:
            result = await self.base_service.toggle_blog_reaction(
                session=session, blog_slug=blog_slug, user_id=user_id, action=action
            )

            if not result:
                return ErrorResponse(message="Blog not found", status_code=HTTP_404_NOT_FOUND)

            return SuccessResponse(message="Blog reaction updated successfully", data=result)
        except Exception as e:
            print(e)
            return ErrorResponse(message="Something went wrong", error=str(e))
