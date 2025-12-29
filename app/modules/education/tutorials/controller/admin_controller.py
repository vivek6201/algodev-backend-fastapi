from sqlmodel.ext.asyncio.session import AsyncSession

from app.common.lib.formatter import ErrorResponse, SuccessResponse

from ..schemas.tutorials import TutorialBase
from ..services.admin_service import AdminService
from .base_controller import BaseController


class AdminController(BaseController):
    def __init__(self):
        self.admin_service = AdminService()

    async def create_tutorial(self, session: AsyncSession, tutorial_data: TutorialBase):
        result = await self.admin_service.create_tutorial(session, tutorial_data)

        if not result["status"]:
            return ErrorResponse(message=result["message"])

        return SuccessResponse(message=result["message"], data=result["data"])

    async def update_tutorial(
        self, session: AsyncSession, tutorial_slug: str, tutorial_data: TutorialBase
    ):
        result = await self.admin_service.update_tutorial(session, tutorial_slug, tutorial_data)

        if not result["status"]:
            return ErrorResponse(message=result["message"])

        return SuccessResponse(message=result["message"])

    async def delete_tutorial(self, session: AsyncSession, tutorial_id: int):
        result = await self.admin_service.delete_tutorial(session, tutorial_id)

        if not result["status"]:
            return ErrorResponse(message=result["message"])

        return SuccessResponse(message=result["message"])
