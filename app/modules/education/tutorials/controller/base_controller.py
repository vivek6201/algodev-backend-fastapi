from typing import Optional

from sqlmodel.ext.asyncio.session import AsyncSession

from app.common.lib.formatter import ErrorResponse, SuccessResponse

from ..schemas.tutorials import NodeResponse, TutorialResponse
from ..services.base_service import BaseService


class BaseController:
    def __init__(self):
        self.base_service = BaseService()

    async def get_tutorials(self, session: AsyncSession, params: dict):
        result = await self.base_service.get_tutorials(session=session, **params)

        if not result:
            return ErrorResponse(message="No tutorials found")

        return SuccessResponse(message="Tutorials fetched successfully", data=result)

    async def get_tutorial(
        self, session: AsyncSession, tutorial_slug: str, is_published: Optional[bool] = None
    ) -> Optional[TutorialResponse]:
        result = await self.base_service.get_tutorial(
            session=session, tutorial_slug=tutorial_slug, is_published=is_published
        )

        if not result:
            return ErrorResponse(message="Tutorial not found")

        return SuccessResponse(message="Tutorial fetched successfully", data=result)

    async def get_node(
        self,
        session: AsyncSession,
        tutorial_slug: str,
        node_slug: str,
        is_published: Optional[bool] = None,
    ) -> Optional[NodeResponse]:
        result = await self.base_service.get_node(
            session=session,
            tutorial_slug=tutorial_slug,
            node_slug=node_slug,
            is_published=is_published,
        )

        if not result:
            return ErrorResponse(message="Node not found")

        return SuccessResponse(message="Node fetched successfully", data=result)
