from typing import Optional

from sqlmodel import Session

from app.common.lib.formatter import SuccessResponse
from app.modules.jobs.models.jobs import JobStatus, ListingType
from app.modules.jobs.services.base_job_service import BaseJobService


class JobController:
    def __init__(self):
        self.job_service = BaseJobService()

    def list_jobs(
        self,
        session: Session,
        status: Optional[JobStatus] = None,
        type: ListingType | None = None,
    ):
        try:
            jobs = self.job_service.list_jobs(session=session, status=status, type=type)
            return SuccessResponse(message="Jobs fetched successfully", data=jobs)
        except Exception as e:
            return e

    def get_job(self, session: Session, job_slug: str, status: Optional[JobStatus] = None):
        job = self.job_service.get_job(session, job_slug, status)
        return SuccessResponse(message="Job fetched successfully", data=job)

    def get_categories(self, session: Session, query: str | None = None):
        categories = self.job_service.get_all_categories(session, query)
        return SuccessResponse(message="Categories fetched successfully", data=categories)
