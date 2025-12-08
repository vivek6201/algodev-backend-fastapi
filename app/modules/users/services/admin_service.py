from typing import Optional

from sqlmodel import select
from sqlmodel.orm.session import Session

from app.modules.users.models.admin import Admin
from app.modules.users.schemas.admin_validations import AdminCreate


class AdminService:
    def get_admin(
        self,
        session: Session,
        admin_id: Optional[int] = None,
        email: Optional[str] = None,
    ):
        if admin_id:
            return session.get(Admin, admin_id)
        if email:
            statement = select(Admin).where(Admin.email == email)
            admin = session.exec(statement).first()
            return admin
        return None

    def create_admin(self, admin_data: AdminCreate, session: Session):
        try:
            admin = Admin(**admin_data.model_dump())
            session.add(admin)
            session.commit()
            session.refresh(admin)
            return admin
        except Exception as e:
            session.rollback()
            raise e

    def update_admin(self, admin_id: int, update_data: dict, session: Session):
        try:
            admin = session.get(Admin, admin_id)
            if not admin:
                return None
            for key, value in update_data.items():
                setattr(admin, key, value)
            session.add(admin)
            session.commit()
            session.refresh(admin)
            return admin
        except Exception as e:
            session.rollback()
            raise e
