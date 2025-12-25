from typing import Optional

from fastapi import HTTPException
from sqlmodel.ext.asyncio.session import AsyncSession

from app.common.lib.formatter import SuccessResponse
from app.modules.jobs.models.jobs import JobStatus, ListingType
from app.modules.jobs.services.base_job_service import BaseJobService


class JobController:
    def __init__(self):
        self.job_service = BaseJobService()

    async def list_jobs(
        self,
        session: AsyncSession,
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

            result = await self.job_service.list_jobs(**params)

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

    async def get_job(
        self, session: AsyncSession, job_slug: str, status: Optional[JobStatus] = None
    ):
        try:
            job = await self.job_service.get_job(session, job_slug, status)
            return SuccessResponse(message="Job fetched successfully", data=job)
        except Exception as e:
            raise HTTPException(status_code=500, detail=str(e))

    async def get_categories(self, session: AsyncSession, query: str | None = None):
        try:
            categories = await self.job_service.get_all_categories(session, query)
            return SuccessResponse(message="Categories fetched successfully", data=categories)
        except Exception as e:
            raise HTTPException(status_code=500, detail=str(e))
