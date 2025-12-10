from fastapi import APIRouter, Depends, Request
from sqlmodel import Session

from app.common.db.config import get_session
from app.common.lib.formatter import TokenPayload
from app.modules.auth.controllers.admin_auth_controller import AdminAuthController
from app.modules.auth.controllers.auth_controller import AuthController
from app.modules.auth.dependencies import ALL_USER_ROLES, RoleChecker
from app.modules.auth.schemas.auth_validations import Login, Signup

auth_router = APIRouter()
auth_controller = AuthController()
admin_auth_controller = AdminAuthController()


@auth_router.post("/login")
def login(body: Login, session: Session = Depends(get_session)):
    return auth_controller.login(body, session)


@auth_router.post("/signup")
def signup(body: Signup, session: Session = Depends(get_session)):
    return auth_controller.signup(body, session)


@auth_router.post("/refresh")
async def refresh_token(request: Request, session: Session = Depends(get_session)):
    return auth_controller.refresh(session, request)


@auth_router.delete("/logout")
def logout(
    session: Session = Depends(get_session),
    current_user: TokenPayload = Depends(RoleChecker(ALL_USER_ROLES)),
):
    return auth_controller.logout(session=session, current_user=current_user)


@auth_router.get("/verify-email/{token}")
def verify_email_link(token: str, session: Session = Depends(get_session)):
    """Verify email via clickable link"""
    return auth_controller.verify_email(token, session)
