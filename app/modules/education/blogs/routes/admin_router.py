from fastapi import APIRouter, Depends
from sqlmodel import Session

from app.common.db.config import get_session
from app.modules.education.blogs.schema.blogs import CreateBlog

admin_router = APIRouter()


@admin_router.get("/", tags=["Blogs"])
def get_blogs(session: Session = Depends(get_session)):
    pass


@admin_router.post("/", tags=["Blogs"])
def create_blog(blog: CreateBlog, session: Session = Depends(get_session)):
    pass


@admin_router.get("/one/{blog_slug}", tags=["Blogs"])
def get_blog(blog_slug: str, session: Session = Depends(get_session)):
    pass


@admin_router.patch("/one/{blog_slug}", tags=["Blogs"])
def update_blog(blog_slug: str, session: Session = Depends(get_session)):
    pass
