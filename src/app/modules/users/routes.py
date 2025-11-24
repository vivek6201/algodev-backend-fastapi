from fastapi import APIRouter, Depends
from sqlmodel import Session

from app.common.db.config import get_session
from app.common.lib.formatter import ErrorResponse, SuccessResponse, TokenPayload
from app.modules.auth.dependencies import ALL_ROLES, RoleChecker
from app.modules.users.controllers.user_controller import UserController
from app.modules.users.schemas.user_validation import UserUpdate

user_router = APIRouter()
user_controller = UserController()


@user_router.get("/{user_id}")
async def get_user(
    user_id: int,
    session: Session = Depends(get_session),
    current_user: TokenPayload = Depends(RoleChecker(ALL_ROLES)),
):
    if current_user.id != user_id:
        raise PermissionError("Unauthorized access to user data")

    user_data = user_controller.get_user(user_id=user_id, session=session)

    if not user_data:
        return ErrorResponse(message="User not found")

    return SuccessResponse(data=user_data, message="User retrieved successfully")


@user_router.put("/{user_id}")
async def update_user(
    user_id: int,
    user_data: UserUpdate,
    session: Session = Depends(get_session),
    current_user: TokenPayload = Depends(RoleChecker(ALL_ROLES)),
):
    if current_user.id != user_id:
        raise PermissionError("Unauthorized access to update user data")

    updated_user = user_controller.update_user(
        user_id=user_id, user_data=user_data, session=session
    )

    if not updated_user:
        return ErrorResponse(message="User not found or update failed")

    return SuccessResponse(data=updated_user, message="User updated successfully")
