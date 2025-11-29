from fastapi import APIRouter, Depends
from sqlmodel.orm.session import Session

from app.common.db.config import get_session
from app.common.lib.formatter import TokenPayload
from app.modules.auth.dependencies import ALL_ADMIN_ROLES, RoleChecker
from app.modules.users.controllers.admin_controller import AdminController

admin_user_router = APIRouter()
admin_controller = AdminController()


@admin_user_router.get("/me")
async def get_me(
    session: Session = Depends(get_session),
    current_admin: TokenPayload = Depends(RoleChecker(ALL_ADMIN_ROLES, user_type="admin")),
):
    return admin_controller.get_admin(session=session, admin_id=current_admin.id)
