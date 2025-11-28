from fastapi.routing import APIRouter

from app.modules.jobs.routes.admin_routes import admin_job_router
from app.modules.jobs.routes.normal_routes import normal_job_router

jobs_router = APIRouter()

jobs_router.include_router(admin_job_router, prefix="/admin", tags=["Admin Jobs"])
jobs_router.include_router(normal_job_router, tags=["Jobs"])
