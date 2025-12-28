from fastapi import APIRouter, Depends
from sqlmodel.ext.asyncio.session import AsyncSession

from app.common.db.config import get_session

admin_router = APIRouter()


@admin_router.post("/")
async def create_tutorial(session: AsyncSession = Depends(get_session)):
    pass
