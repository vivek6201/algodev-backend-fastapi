from sqlmodel import select
from sqlmodel.ext.asyncio.session import AsyncSession

from app.modules.education.shared.model import (
    CategoriesBase,
    EducationCategory,
)


class EducationService:
    async def get_category(self, session: AsyncSession, category_id: int):
        try:
            return await session.get(EducationCategory, category_id)
        except Exception as e:
            raise e

    async def get_categories(self, session: AsyncSession):
        try:
            result = await session.exec(select(EducationCategory))
            return result.all()
        except Exception as e:
            raise e

    async def create_category(self, session: AsyncSession, category_data: CategoriesBase):
        try:
            category = EducationCategory(**category_data.dict())
            session.add(category)
            await session.commit()
            await session.refresh(category)
            return category
        except Exception as e:
            raise e

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

    async def delete_category(self, session: AsyncSession, category_id: int):
        pass
