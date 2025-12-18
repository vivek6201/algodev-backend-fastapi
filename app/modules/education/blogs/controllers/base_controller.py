from typing import Optional

from sqlmodel import Session

from app.common.lib.formatter import ErrorResponse, SuccessResponse

from ..services.base_service import BaseBlogService


class BaseBlogController:
    def __init__(self):
        self.base_service = BaseBlogService()

    def get_blogs(self, session: Session, params: Optional[dict] = None):
        try:
            blogs, total_items = self.base_service.get_blogs(session=session, **params)

            data = {
                "blogs": blogs,
                "page": params.get("page", 1),
                "limit": params.get("limit", 10),
                "total_items": total_items,
            }

            return SuccessResponse(message="Blogs fetched successfully", data=data)

        except Exception as e:
            print(e)
            return ErrorResponse(message="Something went wrong", error=str(e))
