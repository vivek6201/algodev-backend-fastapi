from sqlmodel import Session, select

from app.modules.jobs.models.jobs import Category, Job, JobStatus, ListingType


class BaseJobService:
    def list_jobs(
        self,
        session: Session,
        status: JobStatus,
        type: ListingType | None = None,
    ):
        query = select(Job)
        if status:
            query = query.where(Job.status == status)
        if type:
            query = query.where(Job.listing_type == type)
        return session.exec(query).all()

    def get_job(self, session: Session, job_slug: str, status: JobStatus):
        if status:
            query = select(Job).where(Job.slug == job_slug, Job.status == status)
        else:
            query = select(Job).where(Job.slug == job_slug)

        job = session.exec(query).first()

        return job

    def get_category(
        self, session: Session, category_id: int | None = None, category_name: str | None = None
    ):
        if category_name:
            return session.exec(select(Category).where(Category.name == category_name)).first()

        return session.get(Category, category_id)

    def get_all_categories(self, session: Session):
        return session.exec(select(Category)).all()
