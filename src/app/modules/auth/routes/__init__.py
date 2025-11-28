from fastapi import APIRouter

from app.modules.auth.routes.admin_auth_router import admin_auth_router
from app.modules.auth.routes.auth_router import auth_router as user_auth_router

auth_router = APIRouter()

auth_router.include_router(admin_auth_router, prefix="/admin", tags=["Admin Auth"])
auth_router.include_router(user_auth_router, prefix="", tags=["Auth"])
