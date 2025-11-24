from fastapi import APIRouter
from app.modules.auth.routes import auth_router
from app.modules.jobs.routes import jobs_router
from app.modules.users.routes import user_router

router = APIRouter()

router.include_router(auth_router, prefix="/auth")
router.include_router(jobs_router, prefix="/jobs")
router.include_router(user_router, prefix="/users")