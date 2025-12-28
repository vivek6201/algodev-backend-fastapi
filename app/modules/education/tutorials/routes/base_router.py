from fastapi import APIRouter
from fastapi.param_functions import Depends
from sqlmodel.ext.asyncio.session import AsyncSession

from app.common.db.config import get_session

base_router = APIRouter()


@base_router.get("/")
async def get_all_tutorials(session: AsyncSession = Depends(get_session)):
    pass


@base_router.get("/one/{tutorial_id}")
async def get_tutorial(session: AsyncSession = Depends(get_session)):
    pass
