from fastapi import APIRouter

from .admin_router import admin_router
from .base_router import base_router

tutorial_router = APIRouter()

tutorial_router.include_router(admin_router, prefix="/admin", tags=["Admin Tutorials"])
tutorial_router.include_router(base_router, prefix="", tags=["Tutorials"])
