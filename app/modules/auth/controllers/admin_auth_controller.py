import uuid
from datetime import datetime, timezone

from fastapi import Request
from sqlmodel import select
from sqlmodel.ext.asyncio.session import AsyncSession

from app.common.lib.formatter import ErrorResponse, SuccessResponse, TokenPayload
from app.modules.auth.models.session import AdminSession
from app.modules.auth.schemas.auth_validations import AdminLogin
from app.modules.auth.services.admin_auth_service import AdminAuthService
from app.modules.users.models.admin import Admin
from app.modules.users.services.admin_service import AdminService


class AdminAuthController:
    def __init__(self):
        self.admin_auth_service = AdminAuthService()
        self.admin_service = AdminService()

    async def admin_login(
        self,
        body: AdminLogin,
        session: AsyncSession,
    ):
        try:
            result = await session.exec(select(Admin).where(Admin.email == body.email))
            admin = result.one_or_none()
        except Exception as e:
            print(e)
            return ErrorResponse(message=str(e), status_code=500)

        if not admin:
            return ErrorResponse(message="Admin not found", status_code=404)

        if not self.admin_auth_service.verify_password(body.password, admin.password):
            return ErrorResponse(message="Invalid credentials", status_code=400)

        if admin.id is None:
            return ErrorResponse(message="Admin ID missing", status_code=500)

        # Validate Single Session Policy: Delete all previous sessions
        existing_sessions = await session.exec(
            select(AdminSession).where(AdminSession.admin_id == admin.id)
        )
        for existing_session in existing_sessions.all():
            await session.delete(existing_session)

        # Generate Session ID
        session_id = uuid.uuid4()

        payload = TokenPayload(
            id=admin.id, email=admin.email, role=admin.role, session_id=str(session_id)
        )

        access_token, access_expiry = self.admin_auth_service.create_access_token(payload, 300)
        refresh_token, refresh_expiry = self.admin_auth_service.create_refresh_token(payload, 3600)

        # Create new session
        new_session = AdminSession(
            id=session_id,
            admin_id=admin.id,
            refresh_token=refresh_token,
            expires_at=datetime.fromtimestamp(refresh_expiry / 1000, tz=timezone.utc),
        )
        session.add(new_session)
        await session.commit()

        # Create response object
        return SuccessResponse(
            message="Admin logged in successfully",
            data={
                "user": {
                    "id": admin.id,
                    "email": admin.email,
                    "role": admin.role,
                },
                "tokens": {
                    "access_token": access_token,
                    "expires_in": access_expiry,
                    "refresh_token": refresh_token,
                },
            },
            status_code=200,
        )

    async def admin_logout(
        self, session: AsyncSession, current_admin: TokenPayload, request: Request
    ):
        session_id = current_admin.session_id
        if session_id:
            try:
                # delete specific session by ID
                statement = select(AdminSession).where(AdminSession.id == uuid.UUID(session_id))
                result = await session.exec(statement)
                session_obj = result.first()

                if session_obj:
                    await session.delete(session_obj)
                    await session.commit()
            except Exception:
                pass

        return SuccessResponse(
            message="Admin logged out successfully",
        )

    async def refresh_admin_token(self, session: AsyncSession, request: Request):
        refresh_token = request.cookies.get("admin_refresh_token")

        if not refresh_token:
            refresh_token = request.headers.get("admin_refresh_token")

        if not refresh_token:
            return ErrorResponse(message="Refresh token not found", status_code=401)

        try:
            curr_admin_payload = self.admin_auth_service.verify_token(refresh_token)
        except Exception:
            return ErrorResponse(message="Invalid refresh token", status_code=401)

        # Check expiry
        if (
            curr_admin_payload.get("exp") is not None
            and datetime.fromtimestamp(curr_admin_payload["exp"]) < datetime.now()
        ):
            return ErrorResponse(message="Refresh token has expired", status_code=401)

        admin_id = curr_admin_payload.get("id")
        session_id_str = curr_admin_payload.get("session_id")

        if not session_id_str:
            return ErrorResponse(message="Invalid token payload", status_code=401)

        admin = await self.admin_service.get_admin(session=session, admin_id=admin_id)

        # Validate against session table using ID
        statement = select(AdminSession).where(AdminSession.id == uuid.UUID(session_id_str))
        result = await session.exec(statement)
        session_obj = result.first()

        if not session_obj:
            return ErrorResponse(
                message="Invalid refresh token (session not found)", status_code=401
            )

        if session_obj.refresh_token != refresh_token:
            await session.delete(session_obj)
            await session.commit()
            return ErrorResponse(message="Invalid refresh token (token mismatch)", status_code=401)

        if session_obj.admin_id != admin.id:
            return ErrorResponse(message="Invalid session owner", status_code=401)

        # Delete old session
        await session.delete(session_obj)

        if admin.id is None:
            return ErrorResponse(message="Admin not found", status_code=404)

        # Generate new session ID
        new_session_id = uuid.uuid4()

        payload = TokenPayload(
            id=admin.id, email=admin.email, role=admin.role, session_id=str(new_session_id)
        )

        access_token, access_expiry = self.admin_auth_service.create_access_token(payload, 300)
        new_refresh_token, new_refresh_expiry = self.admin_auth_service.create_refresh_token(
            payload, 3600
        )

        # Create new session
        if admin.id is not None:
            new_session = AdminSession(
                id=new_session_id,
                admin_id=admin.id,
                refresh_token=new_refresh_token,
                expires_at=datetime.fromtimestamp(new_refresh_expiry / 1000, tz=timezone.utc),
            )
            session.add(new_session)
            await session.commit()

        return SuccessResponse(
            message="Token refreshed successfully",
            data={
                "user": {
                    "id": admin.id,
                    "email": admin.email,
                    "role": admin.role,
                },
                "tokens": {
                    "access_token": access_token,
                    "expires_in": access_expiry,
                    "refresh_token": new_refresh_token,
                },
            },
            status_code=200,
        )
