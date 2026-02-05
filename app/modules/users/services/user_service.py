from datetime import datetime
from typing import List, Optional

from sqlmodel import select
from sqlmodel.ext.asyncio.session import AsyncSession

from app.common.cache.decorators import cached, invalidate_cache
from app.modules.users.models.user import Users


class UserService:
    @invalidate_cache(tags=["users_list"])
    async def create_user(self, user_data: dict, session: AsyncSession) -> Users:
        try:
            user = Users(**user_data)
            session.add(user)
            await session.flush()
            await session.refresh(user)
            return user
        except Exception as e:
            await session.rollback()
            raise e

    @invalidate_cache(tags=["users_list"])
    async def delete_user(self, user_id: int, session: AsyncSession) -> bool:
        try:
            user = await session.get(Users, user_id)
            if not user:
                return False
            await session.delete(user)
            await session.commit()
            return True
        except Exception as e:
            await session.rollback()
            raise e
        return True

    @invalidate_cache(tags=["user_{user_id}", "users_list"])
    async def update_user(
        self, user_id: int, update_data: dict, session: AsyncSession
    ) -> Optional[Users]:
        try:
            user = await session.get(Users, user_id)
            if not user:
                return None
            for key, value in update_data.items():
                setattr(user, key, value)
            session.add(user)
            await session.flush()
            await session.refresh(user)
            return user
        except Exception as e:
            await session.rollback()
            raise e

    @cached(key_prefix="users", tags=["user_{user_id}"], response_model=Users)
    async def get_user(
        self,
        session: AsyncSession,
        user_id: Optional[int] = None,
        email: Optional[str] = None,
        username: Optional[str] = None,
        verification_token: Optional[str] = None,
    ) -> Optional[Users]:
        try:
            if user_id:
                return await session.get(Users, user_id)
            if email:
                result = await session.exec(select(Users).where(Users.email == email))
                return result.first()
            if username:
                result = await session.exec(select(Users).where(Users.username == username))
                return result.first()
            if verification_token:
                result = await session.exec(
                    select(Users).where(Users.verification_token == verification_token)
                )
                return result.first()
            return None
        except Exception as e:
            await session.rollback()
            raise e

    @cached(key_prefix="users", tags=["users_list"], response_model=list[Users])
    async def get_all_users(self, session: AsyncSession) -> List[Users]:
        try:
            result = await session.exec(select(Users))
            return list(result.all())
        except Exception as e:
            await session.rollback()
            raise e

    @invalidate_cache(tags=["user_{user_id}", "users_list"])
    async def verify_email(self, token: str, session: AsyncSession) -> bool:
        try:
            # Get user by token
            result = await session.exec(select(Users).where(Users.verification_token == token))
            user = result.first()

            if not user:
                return "Invalid token"

            # Check expiry
            if user.verification_token_expires and user.verification_token_expires < datetime.now():
                return "Token expired"

            # Update user
            user.email_verified = True
            user.verification_token = None
            user.verification_token_expires = None

            session.add(user)
            await session.commit()
            await session.refresh(user)

            return user
        except Exception as e:
            await session.rollback()
            raise e
