from fastapi import Depends, Request
from fastapi.routing import APIRouter
from sqlmodel import Session

from app.common.db.config import get_session
from app.modules.jobs.controllers.job_controller import JobController
from app.modules.jobs.models.jobs import JobStatus, ListingType

normal_job_router = APIRouter()

job_controller = JobController()


@normal_job_router.get("/")
def list_jobs(req: Request, session: Session = Depends(get_session)):
    type: ListingType | None = req.query_params.get("type")
    return job_controller.list_jobs(session, type=type, status=JobStatus.PUBLISHED)


@normal_job_router.get("/one/{job_slug}")
def get_job(job_slug: str, session: Session = Depends(get_session)):
    status = JobStatus.PUBLISHED
    return job_controller.get_job(session, job_slug, status=status)


@normal_job_router.get("/categories")
def get_categories(req: Request, session: Session = Depends(get_session)):
    query: str | None = req.query_params.get("query")
    return job_controller.get_categories(session, query)
