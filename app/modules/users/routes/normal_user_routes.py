from fastapi import APIRouter, Depends
from sqlmodel.ext.asyncio.session import AsyncSession

from app.common.db.config import get_session
from app.common.lib.formatter import ErrorResponse, SuccessResponse, TokenPayload
from app.modules.auth.dependencies import ALL_USER_ROLES, RoleChecker
from app.modules.users.controllers.user_controller import UserController
from app.modules.users.schemas.user_validation import UserUpdate

normal_user_router = APIRouter()
user_controller = UserController()


@normal_user_router.get("/me")
async def get_user(
    session: AsyncSession = Depends(get_session),
    current_user: TokenPayload = Depends(RoleChecker(ALL_USER_ROLES)),
):
    user_data = await user_controller.get_user(user_id=current_user.id, session=session)

    if not user_data:
        return ErrorResponse(message="User not found")

    return SuccessResponse(data=user_data, message="User retrieved successfully")


@normal_user_router.put("/me")
async def update_user(
    user_data: UserUpdate,
    session: AsyncSession = Depends(get_session),
    current_user: TokenPayload = Depends(RoleChecker(ALL_USER_ROLES)),
):
    updated_user = await user_controller.update_user(
        user_id=current_user.id, user_data=user_data, session=session
    )

    if not updated_user:
        return ErrorResponse(message="User not found or update failed")

    return SuccessResponse(data=updated_user, message="User updated successfully")
