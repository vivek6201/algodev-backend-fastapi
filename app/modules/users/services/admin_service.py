from typing import Optional

from sqlmodel import func, select
from sqlmodel.ext.asyncio.session import AsyncSession

from app.common.cache.decorators import cached, invalidate_cache
from app.modules.users.models.admin import Admin
from app.modules.users.schemas.admin_validations import AdminCreate


class AdminService:
    @cached(key_prefix="admin", tags=["admin_{admin_id}"], response_model=Admin)
    async def get_admin(
        self,
        session: AsyncSession,
        admin_id: Optional[int] = None,
        email: Optional[str] = None,
    ):
        try:
            if admin_id:
                return await session.get(Admin, admin_id)
            if email:
                statement = select(Admin).where(Admin.email == email)
                result = await session.exec(statement)
                admin = result.first()
            return admin
        except Exception as e:
            await session.rollback()
            raise e

    async def get_admin_count(self, session: AsyncSession):
        """
        Returns the total count of active admins in the database.
        """
        try:
            result = await session.exec(select(func.count()).select_from(Admin))
            return result.one()
        except Exception as e:
            await session.rollback()
            raise e

    @invalidate_cache(tags=["admin_list"])
    async def create_admin(self, admin_data: AdminCreate, session: AsyncSession):
        try:
            admin = Admin(**admin_data.model_dump())
            session.add(admin)
            await session.commit()
            await session.refresh(admin)
            return admin
        except Exception as e:
            await session.rollback()
            raise e

    @invalidate_cache(tags=["admin_{admin_id}"])
    async def update_admin(self, admin_id: int, update_data: dict, session: AsyncSession):
        try:
            admin = await session.get(Admin, admin_id)
            if not admin:
                return None
            for key, value in update_data.items():
                setattr(admin, key, value)
            session.add(admin)
            await session.commit()
            await session.refresh(admin)
            return admin
        except Exception as e:
            await session.rollback()
            raise e
