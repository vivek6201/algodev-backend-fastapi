from sqlmodel import Session
from starlette.status import HTTP_400_BAD_REQUEST

from app.common.lib.formatter import ErrorResponse, SuccessResponse
from app.modules.education.shared.model import ReactionType
from app.modules.education.shared.services.edu_service import EducationService
from app.modules.education.shared.services.reaction_service import ReactionService


class BaseEducationController:
    def __init__(self):
        self.service = EducationService()
        self.reaction_service = ReactionService()

    def get_categories(self, session: Session):
        try:
            categories = self.service.get_categories(session=session)
            return SuccessResponse(message="Categories fetched successfully", data=categories)
        except Exception as e:
            return ErrorResponse(
                message="Failed to fetch categories", error=e, status_code=HTTP_400_BAD_REQUEST
            )

    def get_user_reaction(self, session: Session, content_slug: str, user_id: int):
        try:
            result = self.reaction_service.get_user_reaction(
                session=session,
                content_slug=content_slug,
                user_id=user_id,
            )

            data = {"like": False, "dislike": False}
            if result:
                if result.reaction == ReactionType.LIKE:
                    data["like"] = True
                elif result.reaction == ReactionType.DISLIKE:
                    data["dislike"] = True

            return SuccessResponse(message="Reaction fetched successfully", data=data)
        except Exception as e:
            return ErrorResponse(
                message="Failed to fetch reaction", error=e, status_code=HTTP_400_BAD_REQUEST
            )
