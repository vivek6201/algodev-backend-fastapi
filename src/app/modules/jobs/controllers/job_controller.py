from sqlmodel import Session

from app.modules.jobs.models.jobs import JobStatus, ListingType
from app.modules.jobs.services.base_job_service import BaseJobService


class JobController:
    def __init__(self):
        self.job_service = BaseJobService()

    def list_jobs(
        self,
        session: Session,
        status: JobStatus,
        type: ListingType | None = None,
    ):
        return self.job_service.list_jobs(session, type, status)

    def get_job(self, session: Session, job_slug: str, status: JobStatus):
        return self.job_service.get_job(session, job_slug, status)

    def get_categories(self, session: Session):
        return self.job_service.get_all_categories(session)
