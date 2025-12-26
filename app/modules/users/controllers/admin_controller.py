from sqlmodel.ext.asyncio.session import AsyncSession

from app.common.lib.formatter import ErrorResponse, SuccessResponse
from app.modules.jobs.services.admin_job_service import AdminJobService
from app.modules.users.services.admin_service import AdminService


class AdminController:
    def __init__(self):
        self.admin_service = AdminService()
        self.job_service = AdminJobService()

    async def get_admin(self, admin_id: int, session: AsyncSession):
        admin = await self.admin_service.get_admin(admin_id=admin_id, session=session)
        data = {
            "id": admin.id,
            "first_name": admin.first_name,
            "last_name": admin.last_name,
            "email": admin.email,
            "role": admin.role,
            "created_at": admin.created_at,
            "updated_at": admin.updated_at,
        }

        return SuccessResponse(message="Admin fetched successfully", data=data)

    async def get_dashboard(self, session: AsyncSession, admin_id: int):
        admin = await self.admin_service.get_admin(session=session, admin_id=admin_id)

        if not admin:
            return ErrorResponse(message="Admin not found", status_code=404)

        total_jobs = await self.job_service.get_all_jobs_count(session=session)
        total_admins = await self.admin_service.get_admin_count(session=session)

        dashboard_data = {"total_jobs": total_jobs, "total_admins": total_admins}

        return SuccessResponse(message="Dashboard data fetched successfully", data=dashboard_data)
