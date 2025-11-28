from fastapi import APIRouter

from app.modules.users.routes.admin_routes import admin_user_router
from app.modules.users.routes.normal_user_routes import normal_user_router

user_router = APIRouter()

user_router.include_router(normal_user_router, prefix="", tags=["Normal User"])
user_router.include_router(admin_user_router, prefix="/admin", tags=["Admin User"])
