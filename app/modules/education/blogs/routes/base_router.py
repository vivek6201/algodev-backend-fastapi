from fastapi import APIRouter, Depends, Request
from sqlmodel import Session

from app.common.db.config import get_session
from app.modules.education.blogs.models.blog import BlogStatus

from ..controllers.base_controller import BaseBlogController

base_router = APIRouter()
base_controller = BaseBlogController()


@base_router.get("/", tags=["Blogs"])
def get_blogs(request: Request, session: Session = Depends(get_session)):
    query_params = request.query_params

    page_param = query_params.get("page", 1)
    limit_param = query_params.get("limit", 10)

    params = {
        "page": int(page_param),
        "limit": int(limit_param),
        "search": query_params.get("search", ""),
        "status": BlogStatus.PUBLISHED,
    }

    return base_controller.get_blogs(session, params=params)
