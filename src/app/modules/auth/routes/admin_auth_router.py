from fastapi import APIRouter, Depends
from sqlmodel import Session

from app.common.db.config import get_session
from app.common.lib.formatter import TokenPayload
from app.modules.auth.controllers.admin_auth_controller import AdminAuthController
from app.modules.auth.dependencies import ALL_ADMIN_ROLES, RoleChecker
from app.modules.auth.schemas.auth_validations import AdminLogin

admin_auth_router = APIRouter()
admin_auth_controller = AdminAuthController()


@admin_auth_router.post("/login")
def admin_login(body: AdminLogin, session: Session = Depends(get_session)):
    return admin_auth_controller.admin_login(body, session)


@admin_auth_router.delete("/logout")
def admin_logout(
    session: Session = Depends(get_session),
    current_admin: TokenPayload = Depends(RoleChecker(ALL_ADMIN_ROLES, user_type="admin")),
):
    return admin_auth_controller.admin_logout(session, current_admin)
