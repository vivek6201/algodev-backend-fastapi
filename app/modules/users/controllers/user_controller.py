from sqlmodel import Session

from app.modules.users.schemas.user_validation import UserUpdate
from app.modules.users.services.user_service import UserService


class UserController:
    def __init__(self):
        self.user_service = UserService()

    def get_user(self, user_id: int, session: Session):
        user = self.user_service.get_user(session, user_id=user_id)
        if not user:
            return None
        response_data = {
            "id": user.id,
            "username": user.username,
            "email": user.email,
            "role": user.role,
            "name": f"{user.first_name} {user.last_name}",
            "created_at": user.created_at,
            "updated_at": user.updated_at,
        }
        return response_data

    def update_user(self, user_id: int, user_data: UserUpdate, session: Session):
        user = self.user_service.update_user(
            user_id=user_id, update_data=user_data.model_dump(exclude_unset=True), session=session
        )
        if not user:
            return None
        response_data = {
            "id": user.id,
            "username": user.username,
            "email": user.email,
            "role": user.role,
            "name": f"{user.first_name} {user.last_name}",
            "created_at": user.created_at,
            "updated_at": user.updated_at,
        }
        return response_data

    def delete_user(self, user_id: int, session: Session):
        return self.user_service.delete_user(user_id=user_id, session=session)
