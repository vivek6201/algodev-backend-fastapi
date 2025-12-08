from sqlalchemy.orm.strategy_options import selectinload
from sqlmodel import Session, select

from app.modules.jobs.models.jobs import Category, Job, JobStatus, ListingType
from app.modules.jobs.schemas.job_validations import JobResponse


class BaseJobService:
    def list_jobs(
        self,
        session: Session,
        status: JobStatus,
        type: ListingType | None = None,
    ):
        try:
            query = select(Job)
            if status:
                query = query.where(Job.status == status)
            if type:
                query = query.where(Job.listing_type == type)
            return session.exec(query).all()
        except Exception as e:
            print(e)
            return None

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
