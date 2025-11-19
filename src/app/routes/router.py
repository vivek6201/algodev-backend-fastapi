from fastapi import APIRouter
from .sub_routes.auth_routes import auth_router
from .sub_routes.jobs_routes import jobs_router
from .sub_routes.user_routes import user_router

router = APIRouter()

router.include_router(auth_router, prefix="/auth")
router.include_router(jobs_router, prefix="/jobs")
router.include_router(user_router, prefix="/users") 