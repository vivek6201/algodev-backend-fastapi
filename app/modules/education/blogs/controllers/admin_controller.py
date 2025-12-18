import math
from typing import Optional

from sqlmodel import Session
from starlette.status import HTTP_404_NOT_FOUND

from app.common.lib.formatter import ErrorResponse, SuccessResponse, TokenPayload
from app.modules.education.blogs.models.blog import BlogStatus
from app.modules.education.blogs.schema.blogs import UpdateBlog
from app.modules.users.services.admin_service import AdminService

from ..schema.blogs import CreateBlog
from ..services.admin_service import AdminBlogService


class AdminBlogController:
    def __init__(self):
        self.admin_blog_service = AdminBlogService()
        self.admin_service = AdminService()

    def get_blogs(self, session: Session, curr_admin: TokenPayload, params: Optional[dict] = None):
        try:
            admin = self.admin_service.get_admin(session=session, admin_id=curr_admin.id)

            if not admin:
                return ErrorResponse(message="Admin not found", status_code=HTTP_404_NOT_FOUND)

            blogs, total_items = self.admin_blog_service.get_blogs(session=session, **params)

            data = {
                "data": blogs,
                "page": params.get("page", 1),
                "limit": params.get("limit", 10),
                "total_items": total_items,
                "total_pages": math.ceil(total_items / params.get("limit", 10)),
            }

            return SuccessResponse(message="Blogs fetched successfully", data=data)
        except Exception as e:
            print(e)
            return ErrorResponse(message="Something went wrong", error=str(e))

    def get_blog(self, session: Session, curr_admin: TokenPayload, blog_slug: str):
        try:
            admin = self.admin_service.get_admin(session=session, admin_id=curr_admin.id)

            if not admin:
                return ErrorResponse(message="Admin not found", status_code=HTTP_404_NOT_FOUND)

            blog = self.admin_blog_service.get_blog_with_details(
                session=session, blog_slug=blog_slug
            )

            if not blog:
                return ErrorResponse(message="Blog not found", status_code=HTTP_404_NOT_FOUND)

            return SuccessResponse(message="Blog fetched successfully", data=blog)
        except Exception as e:
            print(e)
            return ErrorResponse(message="Something went wrong", error=str(e))

    def create_blog(self, session: Session, blog_data: CreateBlog, curr_admin: TokenPayload):
        try:
            admin = self.admin_service.get_admin(session=session, admin_id=curr_admin.id)

            if not admin:
                return ErrorResponse(message="Admin not found", status_code=HTTP_404_NOT_FOUND)

            return self.admin_blog_service.create_blog(session=session, blog_data=blog_data)
        except Exception as e:
            print(e)
            return ErrorResponse(message="Something went wrong", error=str(e))

    def update_blog(
        self, session: Session, blog_slug: str, blog_data: UpdateBlog, curr_admin: TokenPayload
    ):
        try:
            admin = self.admin_service.get_admin(session=session, admin_id=curr_admin.id)

            if not admin:
                return ErrorResponse(message="Admin not found", status_code=HTTP_404_NOT_FOUND)

            blog = self.admin_blog_service.update_blog(
                session=session, blog_slug=blog_slug, blog_data=blog_data
            )

            if not blog:
                return ErrorResponse(message="Blog not found", status_code=HTTP_404_NOT_FOUND)

            return SuccessResponse(message="Blog updated successfully")
        except Exception as e:
            print(e)
            return ErrorResponse(message="Something went wrong", error=str(e))

    def update_blog_status(
        self, session: Session, blog_slug: str, status: BlogStatus, curr_admin: TokenPayload
    ):
        try:
            admin = self.admin_service.get_admin(session=session, admin_id=curr_admin.id)

            if not admin:
                return ErrorResponse(message="Admin not found", status_code=HTTP_404_NOT_FOUND)

            blog = self.admin_blog_service.update_blog(
                session=session, blog_slug=blog_slug, blog_data=UpdateBlog(status=status)
            )

            if not blog:
                return ErrorResponse(message="Blog not found", status_code=HTTP_404_NOT_FOUND)

            return SuccessResponse(message="Blog status updated successfully")
        except Exception as e:
            print(e)
            return ErrorResponse(message="Something went wrong", error=str(e))
