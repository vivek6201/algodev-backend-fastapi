from fastapi import APIRouter, Depends
from sqlmodel.ext.asyncio.session import AsyncSession

from app.common.db.config import get_session
from app.modules.education.shared.controllers.base_controller import BaseEducationController

edu_router = APIRouter()
base_controller = BaseEducationController()


@edu_router.get("/categories")
async def get_categories(session: AsyncSession = Depends(get_session)):
    return await base_controller.get_categories(session=session)
