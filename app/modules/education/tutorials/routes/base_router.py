from fastapi import APIRouter, Request
from fastapi.param_functions import Depends
from sqlmodel.ext.asyncio.session import AsyncSession

from app.common.db.config import get_session
from app.common.lib.formatter import ErrorResponse
from app.modules.education.tutorials.controller.base_controller import BaseController

base_router = APIRouter()
base_controller = BaseController()


@base_router.get("/")
async def get_all_tutorials(request: Request, session: AsyncSession = Depends(get_session)):
    query_params = request.query_params
    limit = int(query_params.get("limit", 10))
    page = int(query_params.get("page", 1))
    search = query_params.get("search", "")
    is_published = query_params.get("is_published", True)

    if limit < 1 or limit > 50:
        return ErrorResponse(message="Limit must be between 1 and 50", status_code=400)

    params = {
        "page": page,
        "limit": limit,
        "search": search,
        "is_published": is_published,
    }

    return await base_controller.get_tutorials(session=session, params=params)


@base_router.get("/one/{tutorial_slug}")
async def get_tutorial(tutorial_slug: str, session: AsyncSession = Depends(get_session)):
    return await base_controller.get_tutorial(
        session=session, tutorial_slug=tutorial_slug, is_published=True
    )


@base_router.get("/node/{tutorial_slug}/{node_slug}")
async def get_node(
    tutorial_slug: str, node_slug: str, session: AsyncSession = Depends(get_session)
):
    return await base_controller.get_node(
        session=session, tutorial_slug=tutorial_slug, node_slug=node_slug, is_published=True
    )
