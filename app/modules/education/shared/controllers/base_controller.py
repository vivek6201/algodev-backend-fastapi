from sqlmodel import Session
from starlette.status import HTTP_400_BAD_REQUEST

from app.common.lib.formatter import ErrorResponse, SuccessResponse
from app.modules.education.shared.services import EducationService


class BaseEducationController:
    def __init__(self):
        self.service = EducationService()

    def get_categories(self, session: Session):
        try:
            categories = self.service.get_categories(session=session)
            return SuccessResponse(message="Categories fetched successfully", data=categories)
        except Exception as e:
            return ErrorResponse(
                message="Failed to fetch categories", error=e, status_code=HTTP_400_BAD_REQUEST
            )
