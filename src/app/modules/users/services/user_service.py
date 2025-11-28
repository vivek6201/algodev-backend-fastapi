from typing import List, Optional

from sqlmodel import Session, select

from app.modules.users.models.user import Users


class UserService:
    def create_user(self, user_data: dict, session: Session) -> Users:
        try:
            user = Users(**user_data)
            session.add(user)
            session.commit()
            session.refresh(user)
            return user
        except Exception as e:
            session.rollback()
            raise e

    def delete_user(self, user_id: int, session: Session) -> bool:
        try:
            user = session.get(Users, user_id)
            if not user:
                return False
            session.delete(user)
            session.commit()
            return True
        except Exception as e:
            session.rollback()
            raise e
        return True

    def update_user(self, user_id: int, update_data: dict, session: Session) -> Optional[Users]:
        try:
            user = session.get(Users, user_id)
            if not user:
                return None
            for key, value in update_data.items():
                setattr(user, key, value)
            session.add(user)
            session.commit()
            session.refresh(user)
            return user
        except Exception as e:
            session.rollback()
            raise e

    def get_user(
        self,
        session: Session,
        user_id: Optional[int] = None,
        email: Optional[str] = None,
        username: Optional[str] = None,
        verification_token: Optional[str] = None,
    ) -> Optional[Users]:
        try:
            if user_id:
                return session.get(Users, user_id)
            if email:
                return session.exec(select(Users).where(Users.email == email)).first()
            if username:
                return session.exec(select(Users).where(Users.username == username)).first()
            if verification_token:
                return session.exec(
                    select(Users).where(Users.verification_token == verification_token)
                ).first()
            return None
        except Exception as e:
            session.rollback()
            raise e

    def get_all_users(self, session: Session) -> List[Users]:
        try:
            return list(session.exec(select(Users)))
        except Exception as e:
            session.rollback()
            raise e
