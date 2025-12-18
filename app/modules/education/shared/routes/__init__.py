from fastapi.routing import APIRouter

from .admin_routes import admin_edu_router
from .base_routes import edu_router

common_router = APIRouter()

common_router.include_router(edu_router, tags=["Common"])
common_router.include_router(admin_edu_router, prefix="/admin", tags=["Admin"])
