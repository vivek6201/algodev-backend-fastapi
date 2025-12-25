from fastapi import APIRouter, Depends
from sqlmodel.ext.asyncio.session import AsyncSession

from app.common.db.config import get_session
from app.common.lib.formatter import TokenPayload
from app.modules.auth.dependencies import ALL_ADMIN_ROLES, RoleChecker
from app.modules.users.controllers.admin_controller import AdminController

admin_user_router = APIRouter()
admin_controller = AdminController()


@admin_user_router.get("/me")
async def get_me(
    session: AsyncSession = Depends(get_session),
    current_admin: TokenPayload = Depends(RoleChecker(ALL_ADMIN_ROLES, user_type="admin")),
):
    return await admin_controller.get_admin(session=session, admin_id=current_admin.id)


@admin_user_router.get("/dashboard")
async def get_dashboard(
    session: AsyncSession = Depends(get_session),
    current_admin: TokenPayload = Depends(RoleChecker(ALL_ADMIN_ROLES, user_type="admin")),
):
    return await admin_controller.get_dashboard(session=session, admin_id=current_admin.id)
