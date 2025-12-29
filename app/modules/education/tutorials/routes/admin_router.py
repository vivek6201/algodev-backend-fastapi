from fastapi import APIRouter, Depends
from sqlmodel.ext.asyncio.session import AsyncSession

from app.common.db.config import get_session
from app.common.lib.formatter import TokenPayload
from app.modules.auth.dependencies import ALL_ADMIN_ROLES, RoleChecker
from app.modules.education.tutorials.controller.admin_controller import AdminController
from app.modules.education.tutorials.schemas.tutorials import TutorialBase

admin_router = APIRouter()
admin_controller = AdminController()


@admin_router.post("/")
async def create_tutorial(
    data: TutorialBase,
    session: AsyncSession = Depends(get_session),
    curr_admin: TokenPayload = Depends(RoleChecker(ALL_ADMIN_ROLES, user_type="admin")),
):
    return admin_controller.create_tutorial(session=session, tutorial_data=data)


@admin_router.patch("/{tutorial_slug}")
async def update_tutorial(
    tutorial_slug: str,
    data: TutorialBase,
    session: AsyncSession = Depends(get_session),
    curr_admin: TokenPayload = Depends(RoleChecker(ALL_ADMIN_ROLES, user_type="admin")),
):
    return admin_controller.update_tutorial(
        session=session, tutorial_slug=tutorial_slug, tutorial_data=data
    )
