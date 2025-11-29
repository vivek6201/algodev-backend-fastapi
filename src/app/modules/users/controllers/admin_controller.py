from sqlalchemy.orm.session import Session

from app.common.lib.formatter import SuccessResponse
from app.modules.users.services.admin_service import AdminService


class AdminController:
    def __init__(self):
        self.admin_service = AdminService()

    def get_admin(self, admin_id: int, session: Session):
        admin = self.admin_service.get_admin(admin_id=admin_id, session=session)
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
