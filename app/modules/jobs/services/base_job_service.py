import math
from typing import Optional

from sqlalchemy.orm.strategy_options import selectinload
from sqlmodel import Session, func, select

from app.modules.jobs.models.jobs import Category, Job, JobStatus, ListingType
from app.modules.jobs.schemas.job_validations import JobResponse


class BaseJobService:
    def list_jobs(
        self,
        session: Session,
        page: int,
        limit: int,
        status: Optional[JobStatus] = None,
        type: ListingType | None = None,
        search: Optional[str] = None,
    ):
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

        total_items = session.exec(count_query).one()
        total_pages = math.ceil(total_items / limit) if limit > 0 else 1

        if page:
            query = query.offset((page - 1) * limit).limit(limit)

        return {
            "jobs": session.exec(query).all(),
            "total_items": total_items,
            "total_pages": total_pages,
        }

    def get_job_instance(
        self, session: Session, job_slug: str, status: JobStatus | None = None
    ) -> Job | None:
        try:
            query = select(Job).where(Job.slug == job_slug)

            if status:
                query = query.where(Job.status == status)

            # LOAD categories
            query = query.options(selectinload(Job.categories))

            return session.exec(query).first()
        except Exception as e:
            print(e)
            return None

    def get_job(
        self, session: Session, job_slug: str, status: JobStatus | None = None
    ) -> JobResponse | None:
        job = self.get_job_instance(session, job_slug, status)
        return JobResponse.model_validate(job) if job else None

    def get_category(
        self, session: Session, category_id: int | None = None, category_name: str | None = None
    ):
        try:
            if category_name:
                return session.exec(select(Category).where(Category.name == category_name)).first()

            return session.get(Category, category_id)
        except Exception as e:
            print(e)
            return None

    def get_all_categories(self, session: Session, query: str | None = None):
        try:
            if query:
                return session.exec(select(Category).where(Category.name.contains(query))).all()
            return session.exec(select(Category)).all()
        except Exception as e:
            print(e)
            return None
