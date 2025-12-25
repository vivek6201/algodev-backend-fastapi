from typing import Optional
from uuid import uuid4

from slugify import slugify
from sqlmodel import func, select
from sqlmodel.ext.asyncio.session import AsyncSession

from app.common.lib.formatter import TokenPayload
from app.modules.jobs.models.jobs import Category, Job, JobStatus
from app.modules.jobs.schemas.category_validations import CategoryCreate, CategoryUpdate
from app.modules.jobs.schemas.job_validations import (
    JobResponse,
    ThirdPartyJobCreate,
    ThirdPartyJobUpdate,
)
from app.modules.jobs.services.base_job_service import BaseJobService


class AdminJobService(BaseJobService):
    async def create_category(self, session: AsyncSession, category_data: CategoryCreate):
        category = await self.get_category(session=session, category_name=category_data.name)
        if category:
            return None

        category = Category(name=category_data.name)
        try:
            session.add(category)
            await session.commit()
            await session.refresh(category)
            return category
        except Exception as e:
            await session.rollback()
            raise e

    async def update_category(
        self, session: AsyncSession, category_id: int, category_data: CategoryUpdate
    ):
        category = await self.get_category(session=session, category_id=category_id)
        if not category:
            return None

        try:
            category.name = category_data.name
            session.add(category)
            await session.commit()
            await session.refresh(category)
            return category
        except Exception as e:
            await session.rollback()
            raise e

    async def create_job(
        self, session: AsyncSession, job_data: ThirdPartyJobCreate, current_admin: TokenPayload
    ):
        if not job_data.slug:
            base_slug = slugify(job_data.title)
            unique_suffix = str(uuid4().hex)[:6]
            job_data.slug = f"{base_slug}-{unique_suffix}"

        job = await self.get_job_instance(session=session, job_slug=job_data.slug, status=None)
        if job:
            return None

        # Bulk fetch categories
        result = await session.exec(select(Category).where(Category.id.in_(job_data.category_id)))
        categories = result.all()

        job_dict = job_data.model_dump(exclude={"category_id"})
        job = Job(**job_dict, admin_id=current_admin.id, categories=categories)

        try:
            session.add(job)
            await session.commit()
            await session.refresh(job)
            return job
        except Exception as e:
            await session.rollback()
            raise e

    async def update_job(
        self,
        session: AsyncSession,
        job_slug: str,
        job_data: ThirdPartyJobUpdate,
    ):
        job = await self.get_job_instance(session=session, job_slug=job_slug, status=None)
        if not job:
            return None

        try:
            job_dict = job_data.model_dump(exclude={"category_id", "slug", "status"})

            for key, value in job_dict.items():
                setattr(job, key, value)

            if job_data.category_id is not None:
                # Fetch new categories
                result = await session.exec(
                    select(Category).where(Category.id.in_(job_data.category_id))
                )
                new_categories = result.all()

                job.categories.clear()
                job.categories.extend(new_categories)

            session.add(job)
            await session.commit()
            await session.refresh(job)
            return JobResponse.model_validate(job)
        except Exception as e:
            await session.rollback()
            raise e

    async def update_job_status(
        self,
        session: AsyncSession,
        job_slug: str,
        status: JobStatus,
    ):
        job = await self.get_job_instance(session=session, job_slug=job_slug, status=None)
        if not job:
            return {
                "status": False,
                "message": "Job not found",
            }

        try:
            job.status = status
            session.add(job)
            await session.commit()
            await session.refresh(job)
            return {
                "status": True,
                "message": "Job status updated successfully",
            }
        except Exception as e:
            await session.rollback()
            raise e

    async def get_all_jobs_count(self, session: AsyncSession, params: Optional[dict] = None):
        query = select(func.count()).select_from(Job)

        if not params:
            result = await session.exec(query)
            return result.one()

        if params.get("status"):
            query = query.where(Job.status == params["status"])
        if params.get("type"):
            query = query.where(Job.listing_type == params["type"])
        if params.get("search"):
            search = params["search"].strip()
            query = query.where(Job.title.ilike(f"%{search}%"))

        result = await session.exec(query)
        count = result.one()
        return count
