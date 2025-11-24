from fastapi import APIRouter
from app.modules.jobs.controllers.jobs_controller import JobsController
from app.common.db.config import get_session
from sqlmodel import Session
from fastapi import Depends
from app.modules.auth.controllers.auth_controller import AuthController
from app.common.lib.formatter import TokenPayload

job_controller = JobsController()
auth_controller = AuthController()

jobs_router = APIRouter()


# @jobs_router.get("/", tags=["Jobs"])
# def list_jobs(session: Session = Depends(get_session), ):
#     return job_controller.list_jobs(session)


# @jobs_router.post("/", tags=["Jobs"])
# def create_job(job_data: dict, session: Session = Depends(get_session), curr_user: TokenPayload = Depends(auth_controller.auth_service.get_current_user)):
#     return job_controller.create_job(session, job_data)
