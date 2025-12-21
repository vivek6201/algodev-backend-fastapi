from typing import Optional

from fastapi import APIRouter, Depends, Request
from sqlmodel import Session

from app.common.db.config import get_session
from app.common.lib.formatter import TokenPayload
from app.modules.auth.dependencies import ALL_USER_ROLES, OptionalRoleChecker, RoleChecker
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


@base_router.get("/one/{blog_slug}", tags=["Blogs"])
def get_blog(blog_slug: str, session: Session = Depends(get_session)):
    return base_controller.get_blog(session, blog_slug=blog_slug)


@base_router.get("/{blog_slug}/metadata", tags=["Blogs"])
def get_blog_metadata(
    blog_slug: str,
    session: Session = Depends(get_session),
    curr_user: Optional[TokenPayload] = Depends(OptionalRoleChecker(allowed_roles=ALL_USER_ROLES)),
):
    user_id = curr_user.id if curr_user else None
    return base_controller.get_blog_metadata(session, blog_slug=blog_slug, user_id=user_id)


@base_router.patch("/{blog_slug}/react", tags=["Blogs"])
def update_blog_reaction(
    blog_slug: str,
    action: str,
    session: Session = Depends(get_session),
    curr_user: TokenPayload = Depends(RoleChecker(allowed_roles=ALL_USER_ROLES)),
):
    return base_controller.update_blog_reaction(
        session, blog_slug=blog_slug, user_id=curr_user.id, action=action
    )
