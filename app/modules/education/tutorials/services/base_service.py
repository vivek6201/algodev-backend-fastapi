from select import select

from sqlmodel.ext.asyncio.session import AsyncSession

from app.common.cache.decorators import cached
from app.common.lib.formatter import ListResponse
from app.modules.education.tutorials.models.tutorials import Tutorial


class BaseService:
    @cached(key_prefix="tutorials", tags=["tutorial_list"], response_model=ListResponse[Tutorial])
    async def get_tutorials(
        self, session: AsyncSession, page: int, limit: int, search: str, is_published: bool
    ) -> ListResponse[Tutorial]:
        search = search.strip()

        statement = select(Tutorial)

        if search:
            statement = statement.where(Tutorial.title.contains(f"%{search}%"))

        if is_published:
            statement = statement.where(Tutorial.is_published == is_published)

        statement = statement.offset((page - 1) * limit).limit(limit)

        result = await session.exec(statement)
        return ListResponse[Tutorial](data=result.all(), page=page, limit=limit)

    @cached(key_prefix="tutorials", tags=["tutorial_{tutorial_slug}"], response_model=Tutorial)
    async def get_tutorial(
        self, session: AsyncSession, tutorial_slug: str, is_published: bool
    ) -> Tutorial:
        statement = select(Tutorial).where(Tutorial.slug == tutorial_slug)

        if is_published:
            statement = statement.where(Tutorial.is_published == is_published)

        result = await session.exec(statement)
        return result.one()
