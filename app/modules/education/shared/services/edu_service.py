from sqlmodel import select
from sqlmodel.ext.asyncio.session import AsyncSession

from app.common.cache.decorators import cached, invalidate_cache
from app.modules.education.shared.model import (
    CategoriesBase,
    EducationCategory,
)


class EducationService:
    @cached(
        key_prefix="edu",
        tags=["edu_category_{category_id}"],
        response_model=EducationCategory,
    )
    async def get_category(self, session: AsyncSession, category_id: int):
        try:
            return await session.get(EducationCategory, category_id)
        except Exception as e:
            raise e

    @cached(key_prefix="edu", tags=["edu_categories"], response_model=EducationCategory)
    async def get_categories(self, session: AsyncSession):
        try:
            result = await session.exec(select(EducationCategory))
            return result.all()
        except Exception as e:
            raise e

    @invalidate_cache(tags=["edu_categories"])
    async def create_category(self, session: AsyncSession, category_data: CategoriesBase):
        try:
            category = EducationCategory(**category_data.dict())
            session.add(category)
            await session.commit()
            await session.refresh(category)
            return category
        except Exception as e:
            raise e

    @invalidate_cache(tags=["edu_categories", "edu_category_{category_id}"])
    async def update_category(
        self, session: AsyncSession, category_id: int, category_data: CategoriesBase
    ):
        try:
            category = await self.get_category(session=session, category_id=category_id)

            if not category:
                return None

            category.name = category_data.name
            session.add(category)
            await session.commit()
            await session.refresh(category)
            return category
        except Exception as e:
            raise e

    @invalidate_cache(tags=["edu_categories", "edu_category_{category_id}"])
    async def delete_category(self, session: AsyncSession, category_id: int):
        pass
