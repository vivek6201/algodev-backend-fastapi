from fastapi import APIRouter
from fastapi.param_functions import Depends
from sqlmodel import Session

from app.common.db.config import get_session
from app.common.lib.formatter import TokenPayload
from app.modules.auth.dependencies import ALL_ADMIN_ROLES, RoleChecker

from ..controllers.admin_controller import AdminEducationController
from ..model import CategoriesBase, EducationCategory

admin_edu_router = APIRouter()
admin_controller = AdminEducationController()


@admin_edu_router.post("/category", response_model=EducationCategory)
def create_category(
    data: CategoriesBase,
    session: Session = Depends(get_session),
    curr_admin: TokenPayload = Depends(RoleChecker(ALL_ADMIN_ROLES, user_type="admin")),
):
    return admin_controller.create_category(
        session=session, category_data=data, curr_admin=curr_admin
    )


@admin_edu_router.patch("/category/{category_id}", response_model=EducationCategory)
def update_category(
    data: CategoriesBase,
    category_id: int,
    session: Session = Depends(get_session),
    curr_admin: TokenPayload = Depends(RoleChecker(ALL_ADMIN_ROLES, user_type="admin")),
):
    return admin_controller.update_category(
        session=session, category_id=category_id, category_data=data, curr_admin=curr_admin
    )


@admin_edu_router.delete("/category/{category_id}")
def delete_category():
    pass
