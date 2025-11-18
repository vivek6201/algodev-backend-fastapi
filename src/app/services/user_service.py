from typing import Optional, List
from sqlmodel import Session, select
from app.db.models.user import User
from app.db.config import get_session

class UserService:
	def create_user(self, user_data: dict, session: Session) -> User:
		user = User(**user_data)
		session.add(user)
		session.commit()
		session.refresh(user)
		return user

	def delete_user(self, user_id: int, session: Session) -> bool:
		user = session.get(User, user_id)
		if not user:
			return False
		session.delete(user)
		session.commit()
		return True

	def update_user(self, user_id: int, update_data: dict, session: Session) -> Optional[User]:
		user = session.get(User, user_id)
		if not user:
			return None
		for key, value in update_data.items():
			setattr(user, key, value)
		session.add(user)
		session.commit()
		session.refresh(user)
		return user

	def get_user(self, session: Session, user_id: Optional[int] = None, email: Optional[str] = None, username: Optional[str] = None) -> Optional[User]:
		if user_id:
			return session.get(User, user_id)
		if email:
			return session.exec(select(User).where(User.email == email)).first()
		if username:
			return session.exec(select(User).where(User.username == username)).first()
		return None

	def get_all_users(self, session: Session) -> List[User]:
		return list(session.exec(select(User)))
