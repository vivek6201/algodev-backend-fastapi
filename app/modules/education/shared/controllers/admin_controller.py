from fastapi.param_functions import Depends
from sqlmodel import Session
from starlette.status import HTTP_400_BAD_REQUEST, HTTP_404_NOT_FOUND

from app.common.lib.formatter import ErrorResponse, SuccessResponse, TokenPayload
from app.modules.auth.dependencies import ALL_ADMIN_ROLES, RoleChecker
from app.modules.education.shared.controllers.base_controller import BaseEducationController
from app.modules.education.shared.services.edu_service import EducationService
from app.modules.users.services.admin_service import AdminService

from ..model import CategoriesBase


class AdminEducationController(BaseEducationController):
    def __init__(self):
        self.service = EducationService()
        self.admin_service = AdminService()

    def create_category(
        self, session: Session, category_data: CategoriesBase, curr_admin: TokenPayload
    ):
        admin = self.admin_service.get_admin(session=session, admin_id=curr_admin.id)

        if not admin:
            return ErrorResponse(message="Admin not found", status_code=HTTP_404_NOT_FOUND)

        category = self.service.create_category(session=session, category_data=category_data)

        if not category:
            return ErrorResponse(
                message="Failed to create category", status_code=HTTP_400_BAD_REQUEST
            )

        return SuccessResponse(message="Category created successfully", data=category)

    def update_category(
        self,
        session: Session,
        category_id: int,
        category_data: CategoriesBase,
        curr_admin: TokenPayload = Depends(RoleChecker(ALL_ADMIN_ROLES, user_type="admin")),
    ):
        admin = self.admin_service.get_admin(session=session, admin_id=curr_admin.id)

        if not admin:
            return ErrorResponse(message="Admin not found", status_code=HTTP_404_NOT_FOUND)

        category = self.service.update_category(
            session=session, category_id=category_id, category_data=category_data
        )

        if not category:
            return ErrorResponse(
                message="Failed to update category", status_code=HTTP_400_BAD_REQUEST
            )

        return SuccessResponse(message="Category updated successfully", data=category)
