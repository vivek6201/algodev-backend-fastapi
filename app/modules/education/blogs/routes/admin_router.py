from fastapi import APIRouter, Body, Depends, Request
from sqlmodel import Session

from app.common.db.config import get_session
from app.common.lib.formatter import TokenPayload
from app.modules.auth.dependencies import ALL_ADMIN_ROLES, RoleChecker
from app.modules.education.blogs.controllers.admin_controller import AdminBlogController
from app.modules.education.blogs.models.blog import BlogStatus
from app.modules.education.blogs.schema.blogs import CreateBlog, UpdateBlog

admin_router = APIRouter()
admin_controller = AdminBlogController()


@admin_router.get("/", tags=["Blogs"])
def get_blogs(
    request: Request,
    session: Session = Depends(get_session),
    curr_admin: TokenPayload = Depends(RoleChecker(ALL_ADMIN_ROLES, user_type="admin")),
):
    query_params = request.query_params

    page_param = query_params.get("page", 1)
    limit_param = query_params.get("limit", 10)

    params = {
        "page": int(page_param),
        "limit": int(limit_param),
        "search": query_params.get("search", ""),
    }

    return admin_controller.get_blogs(session, curr_admin=curr_admin, params=params)


@admin_router.post("/", tags=["Blogs"])
def create_blog(
    blog_data: CreateBlog,
    session: Session = Depends(get_session),
    curr_admin: TokenPayload = Depends(RoleChecker(ALL_ADMIN_ROLES, user_type="admin")),
):
    return admin_controller.create_blog(session=session, blog_data=blog_data, curr_admin=curr_admin)


@admin_router.get("/one/{blog_slug}", tags=["Blogs"])
def get_blog(
    blog_slug: str,
    session: Session = Depends(get_session),
    curr_admin: TokenPayload = Depends(RoleChecker(ALL_ADMIN_ROLES, user_type="admin")),
):
    return admin_controller.get_blog(session=session, blog_slug=blog_slug, curr_admin=curr_admin)


@admin_router.patch("/one/{blog_slug}", tags=["Blogs"])
def update_blog(
    blog_slug: str,
    blog_data: UpdateBlog,
    session: Session = Depends(get_session),
    curr_admin: TokenPayload = Depends(RoleChecker(ALL_ADMIN_ROLES, user_type="admin")),
):
    return admin_controller.update_blog(
        session=session, blog_slug=blog_slug, blog_data=blog_data, curr_admin=curr_admin
    )


@admin_router.patch("/publish/{blog_slug}", tags=["Blogs"])
def publish_blog(
    blog_slug: str,
    status: BlogStatus = Body(embed=True),
    session: Session = Depends(get_session),
    curr_admin: TokenPayload = Depends(RoleChecker(["SUPER_ADMIN", "ADMIN"], user_type="admin")),
):
    return admin_controller.update_blog_status(
        session=session, blog_slug=blog_slug, status=status, curr_admin=curr_admin
    )
