from fastapi import APIRouter

from app.modules.auth.routes import auth_router
from app.modules.common.routes import common_router
from app.modules.education.routes import education_router
from app.modules.jobs.routes import jobs_router
from app.modules.users.routes import user_router

router = APIRouter()

router.include_router(auth_router, prefix="/auth", tags=["Authentication"])
router.include_router(jobs_router, prefix="/jobs", tags=["Jobs"])
router.include_router(user_router, prefix="/users", tags=["Users"])
router.include_router(common_router, prefix="/common", tags=["Common"])
router.include_router(education_router, prefix="/edu", tags=["Education"])
