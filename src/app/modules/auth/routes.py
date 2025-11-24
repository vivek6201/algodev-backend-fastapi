from fastapi import APIRouter, Depends, Request
from sqlmodel import Session

from app.common.db.config import get_session
from app.common.lib.formatter import TokenPayload
from app.modules.auth.controllers.auth_controller import AuthController
from app.modules.auth.dependencies import ALL_ROLES, RoleChecker
from app.modules.auth.schemas.auth_validations import Login, Signup

auth_router = APIRouter()
auth_controller = AuthController()


@auth_router.post("/login")
def login(body: Login, session: Session = Depends(get_session)):
    return auth_controller.login(body, session)


@auth_router.post("/signup")
def signup(body: Signup, session: Session = Depends(get_session)):
    return auth_controller.signup(body, session)


@auth_router.post("/refresh-token")
async def refresh_token(request: Request, session: Session = Depends(get_session)):
    return auth_controller.refresh(session, request)


@auth_router.post("/logout/{user_id}")
def logout(
    user_id: int,
    session: Session = Depends(get_session),
    current_user: TokenPayload = Depends(RoleChecker(ALL_ROLES)),
):
    return auth_controller.logout(user_id=user_id, session=session, current_user=current_user)


@auth_router.get("/verify-email/{token}")
def verify_email_link(token: str, session: Session = Depends(get_session)):
    """Verify email via clickable link (GET request)"""
    return auth_controller.verify_email(token, session)
