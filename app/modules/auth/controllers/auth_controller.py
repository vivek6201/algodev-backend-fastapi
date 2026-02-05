import secrets
import uuid
from datetime import datetime, timedelta, timezone
from pathlib import Path

from fastapi import BackgroundTasks, Request
from sqlmodel import select
from sqlmodel.ext.asyncio.session import AsyncSession

from app.common.lib.formatter import ErrorResponse, SuccessResponse, TokenPayload
from app.config.settings import settings
from app.modules.auth.models.session import Session
from app.modules.auth.schemas.auth_validations import Login
from app.modules.auth.services.auth_service import AuthService
from app.modules.common.services.email_service import email_service
from app.modules.users.models.user import Users
from app.modules.users.services.user_service import UserService


class AuthController:
    def __init__(self):
        self.auth_service = AuthService()
        self.user_service = UserService()

    async def signup(self, user: Users, background_tasks: BackgroundTasks, session: AsyncSession):
        # Check if user already exists
        existing_user = await self.user_service.get_user(
            session=session, email=user.email, username=user.username
        )
        if existing_user:
            return ErrorResponse(message="User already exists", status_code=400)

        # Generate verification token
        verification_token = secrets.token_urlsafe(32)
        verification_expires = (datetime.now(timezone.utc) + timedelta(hours=24)).replace(
            tzinfo=None
        )

        # Hash password
        hashed_password = self.auth_service.hash_password(user.password)

        # Prepare user data
        user_data = user.model_dump()
        user_data.update(
            {
                "password": hashed_password,
                "verification_token": verification_token,
                "verification_token_expires": verification_expires,
                "email_verified": False,
            }
        )

        try:
            # Create user
            new_user = await self.user_service.create_user(user_data, session)

            if new_user is None or new_user.id is None:
                await session.rollback()
                return ErrorResponse(message="Failed to create user", status_code=500)

            # Prepare Email
            template_path = Path("app/modules/common/email-templates/verify-email.html")
            if not template_path.exists():
                # Fallback or log error? User requested "create user must fail if template missing"?
                # The user code had: if not template_path.exists(): return ErrorResponse
                await session.rollback()
                return ErrorResponse(message="Email template not found", status_code=500)

            template_content = template_path.read_text(encoding="utf-8")

            verification_link = f"{settings.USER_APP_URL}/verify-email?token={verification_token}"

            html_content = template_content.replace(
                "{{name}}", f"{new_user.first_name} {new_user.last_name}"
            )
            html_content = html_content.replace("{{verify_link}}", verification_link)

            # Add background task
            background_tasks.add_task(
                email_service.send_mail,
                recievers_list=[new_user.email],
                subject="Verify your email - Algorithmic Dev",
                html=html_content,
            )

            await session.commit()
            return SuccessResponse(
                message="User created successfully. Please verify your email.",
                data={
                    "user_id": new_user.id,
                    "email": new_user.email,
                    "role": new_user.role,
                    "message": "Verification token has been sent to your email.",
                },
                status_code=201,
            )

        except Exception as e:
            await session.rollback()
            return ErrorResponse(message=str(e), status_code=500)

    async def login(self, body: Login, session: AsyncSession):
        try:
            user = await self.user_service.get_user(
                session=session, email=body.email, username=body.username
            )
        except Exception as e:
            return ErrorResponse(message=str(e), status_code=500)

        if not user:
            return ErrorResponse(message="User not found", status_code=404)

        if not self.auth_service.verify_password(body.password, user.password):
            return ErrorResponse(message="Invalid credentials", status_code=400)

        # Enforce Max Sessions Policy
        if user.id is not None:
            active_sessions_result = await session.exec(
                select(Session).where(Session.user_id == user.id).order_by(Session.created_at.asc())
            )
            active_sessions = active_sessions_result.all()

            # If current sessions >= max_sessions, remove oldest ones
            # We are about to add 1 more, so if we have N sessions and limit is N, we need to remove at least 1.
            # Wait, if we are at limit, we remove (count - limit + 1)

            current_count = len(active_sessions)
            sessions_to_delete = 0

            if current_count >= user.max_sessions:
                sessions_to_delete = current_count - user.max_sessions + 1

            if sessions_to_delete > 0:
                for i in range(sessions_to_delete):
                    await session.delete(active_sessions[i])

        # Generate Session ID
        session_id = uuid.uuid4()

        if user.id is None:
            return ErrorResponse(message="User ID is missing", status_code=500)

        payload = TokenPayload(
            id=user.id, email=user.email, role=user.role, session_id=str(session_id)
        )

        access_token, access_expiry = self.auth_service.create_access_token(payload)
        refresh_token, refresh_expiry = self.auth_service.create_refresh_token(payload)

        # Create new session
        new_session = Session(
            id=session_id,
            user_id=user.id,
            refresh_token=refresh_token,
            expires_at=datetime.fromtimestamp(refresh_expiry / 1000, tz=timezone.utc),
            user_agent=None,  # context needed
            ip_address=None,  # context needed
        )
        session.add(new_session)
        await session.commit()

        # Create response object
        return SuccessResponse(
            message="User logged in successfully",
            data={
                "user": {
                    "id": user.id,
                    "email": user.email,
                    "first_name": user.first_name,
                    "last_name": user.last_name,
                    "username": user.username,
                    "role": user.role,
                },
                "tokens": {
                    "access_token": access_token,
                    "expires_in": access_expiry,
                    "refresh_token": refresh_token,
                },
            },
            status_code=200,
        )

    async def verify_email(self, token: str, session: AsyncSession):
        try:
            result = await self.user_service.verify_email(token, session)

            if isinstance(result, str):
                return ErrorResponse(message=result, status_code=400)

            return SuccessResponse(message="Email verified successfully", status_code=200)
        except Exception as e:
            return ErrorResponse(message=str(e), status_code=500)

    async def logout(self, session: AsyncSession, request: Request, current_user: TokenPayload):
        session_id = current_user.session_id
        if session_id:
            try:
                # Delete by Session ID
                statement = select(Session).where(Session.id == uuid.UUID(session_id))
                result = await session.exec(statement)
                session_obj = result.first()

                if session_obj:
                    await session.delete(session_obj)
                    await session.commit()
            except Exception:
                pass

        return SuccessResponse(
            message="User logged out successfully",
        )

    async def refresh(self, request: Request, session: AsyncSession):
        refresh_token = request.cookies.get("refresh_token")

        if not refresh_token:
            refresh_token = request.headers.get("refresh_token")

        if not refresh_token:
            return ErrorResponse(message="Refresh token not found", status_code=401)

        try:
            curr_user_payload = self.auth_service.verify_token(refresh_token)
        except Exception:
            return ErrorResponse(message="Invalid refresh token", status_code=401)

        # Check expiry
        if (
            curr_user_payload.get("exp") is not None
            and datetime.fromtimestamp(curr_user_payload["exp"]) < datetime.now()
        ):
            return ErrorResponse(message="Refresh token has expired", status_code=401)

        user_id = curr_user_payload.get("id")
        session_id_str = curr_user_payload.get("session_id")

        if not session_id_str:
            return ErrorResponse(message="Invalid token payload", status_code=401)

        user = await self.user_service.get_user(session=session, user_id=user_id)

        # Validate against session table using ID
        statement = select(Session).where(Session.id == uuid.UUID(session_id_str))
        result = await session.exec(statement)
        session_obj = result.first()

        if not session_obj:
            return ErrorResponse(
                message="Invalid refresh token (session not found)", status_code=401
            )

        # Verify strict token match for security (detect reuse)
        if session_obj.refresh_token != refresh_token:
            # Logic for reused token attack detection -> invalidate all user sessions?
            # For now just fail.
            await session.delete(session_obj)  # Delete compromised session
            await session.commit()
            return ErrorResponse(message="Invalid refresh token (token mismatch)", status_code=401)

        if session_obj.user_id != user.id:
            return ErrorResponse(message="Invalid session owner", status_code=401)

        # Delete old session (Rotation)
        await session.delete(session_obj)

        if user.id is None:
            return ErrorResponse(message="User ID is missing", status_code=400)

        # Generate new Session ID
        new_session_id = uuid.uuid4()

        payload: TokenPayload = TokenPayload(
            id=user.id, email=user.email, role=user.role, session_id=str(new_session_id)
        )

        # Create new tokens
        access_token, access_expiry = self.auth_service.create_access_token(payload)
        new_refresh_token, new_refresh_expiry = self.auth_service.create_refresh_token(payload)

        # Create new session (rotate)
        new_session = Session(
            id=new_session_id,
            user_id=user.id,
            refresh_token=new_refresh_token,
            expires_at=datetime.fromtimestamp(new_refresh_expiry / 1000, tz=timezone.utc),
        )
        session.add(new_session)
        await session.commit()

        return SuccessResponse(
            message="Token refreshed successfully",
            data={
                "user": {
                    "id": user.id,
                    "email": user.email,
                    "first_name": user.first_name,
                    "last_name": user.last_name,
                    "username": user.username,
                    "role": user.role,
                },
                "tokens": {
                    "access_token": access_token,
                    "expires_in": access_expiry,
                    "refresh_token": new_refresh_token,
                },
            },
            status_code=200,
        )
