from sqlmodel.ext.asyncio.session import AsyncSession

from app.modules.education.tutorials.services.base_service import BaseService


class BaseController:
    def __init__(self):
        self.base_service = BaseService()

    async def get_tutorials(self, session: AsyncSession, params: dict):
        return await self.base_service.get_tutorials(session=session, **params)

    async def get_tutorial(self, session: AsyncSession, tutorial_slug: str, is_published: bool):
        return await self.base_service.get_tutorial(
            session=session, tutorial_slug=tutorial_slug, is_published=is_published
        )
