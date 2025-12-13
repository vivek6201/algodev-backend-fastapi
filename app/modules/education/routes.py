from fastapi import APIRouter

from .blogs.routes import blog_router
from .tutorials.routes import tutorial_router

education_router = APIRouter()

education_router.include_router(blog_router, prefix="/blogs", tags=["Blogs"])
education_router.include_router(tutorial_router, prefix="/tutorials", tags=["Tutorials"])
