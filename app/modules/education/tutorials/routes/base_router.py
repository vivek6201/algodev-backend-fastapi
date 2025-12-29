from fastapi import APIRouter, Request
from fastapi.param_functions import Depends
from sqlmodel.ext.asyncio.session import AsyncSession

from app.common.db.config import get_session
from app.modules.education.tutorials.controller.base_controller import BaseController

base_router = APIRouter()
base_controller = BaseController()


@base_router.get("/")
async def get_all_tutorials(request: Request, session: AsyncSession = Depends(get_session)):
    query_params = request.query_params
    params = {
        "page": query_params.get("page", 1),
        "limit": query_params.get("limit", 10),
        "search": query_params.get("search", ""),
        "is_published": query_params.get("is_published", True),
    }

    return await base_controller.get_tutorials(session=session, params=params)


@base_router.get("/one/{tutorial_slug}")
async def get_tutorial(tutorial_slug: str, session: AsyncSession = Depends(get_session)):
    return await base_controller.get_tutorial(session=session, tutorial_slug=tutorial_slug)
