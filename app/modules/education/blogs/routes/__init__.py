from fastapi import APIRouter

from .admin_router import admin_router
from .base_router import base_router

blog_router = APIRouter()

blog_router.include_router(admin_router, prefix="/admin", tags=["Admin Blogs"])
blog_router.include_router(base_router, prefix="", tags=["Blogs"])
