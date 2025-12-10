from typing import Optional

from fastapi import HTTPException
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
        page: int,
        limit: int,
        search: Optional[str] = None,
        status: Optional[JobStatus] = None,
        type: Optional[ListingType] = None,
    ):
        try:
            params = {
                "session": session,
                "status": status,
                "type": type,
                "page": page,
                "limit": limit,
                "search": search,
            }

            result = self.job_service.list_jobs(**params)

            return SuccessResponse(
                message="Jobs fetched successfully",
                data={
                    "data": result["jobs"],
                    "page": page,
                    "limit": limit,
                    "total_items": result["total_items"],
                    "total_pages": result["total_pages"],
                },
            )
        except Exception as e:
            raise HTTPException(status_code=500, detail=str(e))

    def get_job(self, session: Session, job_slug: str, status: Optional[JobStatus] = None):
        try:
            job = self.job_service.get_job(session, job_slug, status)
            return SuccessResponse(message="Job fetched successfully", data=job)
        except Exception as e:
            raise HTTPException(status_code=500, detail=str(e))

    def get_categories(self, session: Session, query: str | None = None):
        try:
            categories = self.job_service.get_all_categories(session, query)
            return SuccessResponse(message="Categories fetched successfully", data=categories)
        except Exception as e:
            raise HTTPException(status_code=500, detail=str(e))
