from select import select

from slugify.slugify import slugify
from sqlmodel.ext.asyncio.session import AsyncSession

from app.common.cache.decorators import invalidate_cache
from app.common.db.config import logger
from app.modules.education.shared.model import EducationCategory

from ..models.tutorials import Tutorial
from ..schemas.tutorials import TutorialBase
from .base_service import BaseService


class AdminService(BaseService):
    @invalidate_cache(tags=["tutorial_list"])
    async def create_tutorial(self, session: AsyncSession, tutorial_data: TutorialBase):
        if not tutorial_data.slug:
            tutorial_data.slug = slugify(tutorial_data.title)

        tutorial = self.get_tutorial(session=session, tutorial_slug=tutorial_data.slug)

        if tutorial:
            return {
                "message": "Tutorial already exists",
                "status": False,
            }

        result = await session.exec(
            select(EducationCategory).where(EducationCategory.id.in_(tutorial_data.categories))
        )
        categories = result.all()

        tutorial_dict = tutorial_data.model_dump(exclude={"categories"})

        tutorial = Tutorial(**tutorial_dict)
        tutorial.categories = categories

        try:
            session.add(tutorial)
            await session.commit()
            await session.refresh(tutorial)
            return {
                "message": "Tutorial created successfully",
                "status": True,
                "data": tutorial,
            }
        except Exception as e:
            await session.rollback()
            logger.exception(e)
            return {
                "message": "Something went wrong",
                "status": False,
            }
