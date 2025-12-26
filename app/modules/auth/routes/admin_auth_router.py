from fastapi import APIRouter, Depends, Request
from sqlmodel.ext.asyncio.session import AsyncSession

from app.common.db.config import get_session
from app.common.lib.formatter import TokenPayload
from app.modules.auth.controllers.admin_auth_controller import AdminAuthController
from app.modules.auth.dependencies import ALL_ADMIN_ROLES, RoleChecker
from app.modules.auth.schemas.auth_validations import AdminLogin

admin_auth_router = APIRouter()
admin_auth_controller = AdminAuthController()


@admin_auth_router.post("/login")
async def admin_login(body: AdminLogin, session: AsyncSession = Depends(get_session)):
    return await admin_auth_controller.admin_login(body, session)


@admin_auth_router.delete("/logout")
async def admin_logout(
    session: AsyncSession = Depends(get_session),
    current_admin: TokenPayload = Depends(RoleChecker(ALL_ADMIN_ROLES, user_type="admin")),
):
    return await admin_auth_controller.admin_logout(session, current_admin)


@admin_auth_router.post("/refresh")
async def refresh_admin_token(
    request: Request,
    session: AsyncSession = Depends(get_session),
):
    return await admin_auth_controller.refresh_admin_token(session, request)
