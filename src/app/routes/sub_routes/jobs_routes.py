from fastapi import APIRouter
from app.controllers.jobs_controller import JobsController

job_controller = JobsController

jobs_router = APIRouter()