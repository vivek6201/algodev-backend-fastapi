from fastapi import APIRouter, BackgroundTasks, Depends, Request
from sqlmodel.ext.asyncio.session import AsyncSession

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
async def login(body: Login, session: AsyncSession = Depends(get_session)):
    return await auth_controller.login(body, session)


@auth_router.post("/signup", tags=["Auth"])
async def signup(
    signup_data: Signup,
    background_tasks: BackgroundTasks,
    session: AsyncSession = Depends(get_session),
):
    return await auth_controller.signup(
        user=signup_data, session=session, background_tasks=background_tasks
    )


@auth_router.post("/refresh")
async def refresh_token(request: Request, session: AsyncSession = Depends(get_session)):
    return await auth_controller.refresh(request, session)


@auth_router.post("/logout")
async def logout(
    request: Request,
    session: AsyncSession = Depends(get_session),
    current_user: TokenPayload = Depends(RoleChecker(ALL_USER_ROLES)),
):
    return await auth_controller.logout(session=session, current_user=current_user, request=request)


@auth_router.get("/verify-email/{token}")
async def verify_email_link(token: str, session: AsyncSession = Depends(get_session)):
    """Verify email via clickable link"""
    return await auth_controller.verify_email(token, session)
