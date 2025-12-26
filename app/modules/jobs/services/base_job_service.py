import math
from typing import Optional

from sqlalchemy.orm.strategy_options import selectinload
from sqlmodel import func, select
from sqlmodel.ext.asyncio.session import AsyncSession

from app.common.cache.decorators import cached
from app.common.lib.formatter import ListResponse
from app.modules.jobs.models.jobs import Category, Job, JobStatus, ListingType
from app.modules.jobs.schemas.category_validations import CategoryResponse
from app.modules.jobs.schemas.job_validations import CompactJobResponse, JobResponse


class BaseJobService:
    @cached(
        key_prefix="jobs",
        tags=["jobs_list"],
        response_model=ListResponse[CompactJobResponse],
    )
    async def list_jobs(
        self,
        session: AsyncSession,
        page: int,
        limit: int,
        status: Optional[JobStatus] = None,
        type: ListingType | None = None,
        search: Optional[str] = None,
    ) -> ListResponse[CompactJobResponse]:
        query = select(Job)
        count_query = select(func.count()).select_from(Job)

        if status:
            query = query.where(Job.status == status)
            count_query = count_query.where(Job.status == status)
        if type:
            query = query.where(Job.listing_type == type)
            count_query = count_query.where(Job.listing_type == type)
        if search:
            search = search.strip()
            query = query.where(Job.title.ilike(f"%{search}%"))
            count_query = count_query.where(Job.title.ilike(f"%{search}%"))

        result = await session.exec(count_query)
        total_items = result.one()
        total_pages = math.ceil(total_items / limit) if limit > 0 else 1

        if page:
            query = query.offset((page - 1) * limit).limit(limit)

        result = await session.exec(query)
        return ListResponse[CompactJobResponse](
            data=result.all(),
            total_items=total_items,
            total_pages=total_pages,
        )

    async def get_job_instance(
        self, session: AsyncSession, job_slug: str, status: JobStatus | None = None
    ) -> Job | None:
        try:
            query = select(Job).where(Job.slug == job_slug)

            if status:
                query = query.where(Job.status == status)

            # LOAD categories
            query = query.options(selectinload(Job.categories))

            result = await session.exec(query)
            return result.first()
        except Exception as e:
            print(e)
            return None

    @cached(
        key_prefix="jobs",
        tags=["job_{job_slug}"],
        response_model=JobResponse,
    )
    async def get_job(
        self, session: AsyncSession, job_slug: str, status: JobStatus | None = None
    ) -> JobResponse | None:
        job = await self.get_job_instance(session, job_slug, status)
        return JobResponse.model_validate(job) if job else None

    @cached(
        key_prefix="category",
        tags=["category_{category_id}"],
        response_model=CategoryResponse,
    )
    async def get_category(
        self,
        session: AsyncSession,
        category_id: int | None = None,
        category_name: str | None = None,
    ):
        try:
            if category_name:
                result = await session.exec(select(Category).where(Category.name == category_name))
                return result.first()

            return await session.get(Category, category_id)
        except Exception as e:
            print(e)
            return None

    @cached(
        key_prefix="categories",
        tags=["categories", "categories_list"],
        response_model=CategoryResponse,
    )
    async def get_all_categories(self, session: AsyncSession, query: str | None = None):
        try:
            if query:
                result = await session.exec(select(Category).where(Category.name.contains(query)))
                return result.all()
            result = await session.exec(select(Category))
            return result.all()
        except Exception as e:
            print(e)
            return None
