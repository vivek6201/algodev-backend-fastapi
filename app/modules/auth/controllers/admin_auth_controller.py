from fastapi import Request
from sqlmodel import select
from sqlmodel.ext.asyncio.session import AsyncSession

from app.common.lib.formatter import ErrorResponse, SuccessResponse, TokenPayload
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

        payload = TokenPayload(
            id=admin.id,
            email=admin.email,
            role=admin.role,
        )

        access_token, access_expiry = self.admin_auth_service.create_access_token(payload, 300)
        refresh_token, _ = self.admin_auth_service.create_refresh_token(payload, 3600)

        if admin.id is not None:
            await self.admin_service.update_admin(
                admin.id, {"refresh_token": refresh_token}, session
            )

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

    async def admin_logout(self, session: AsyncSession, current_admin: TokenPayload):
        admin = await self.admin_service.get_admin(admin_id=current_admin.id, session=session)

        if not admin:
            return ErrorResponse(message="Admin not found", status_code=404)

        if admin.id is not None:
            await self.admin_service.update_admin(admin.id, {"refresh_token": None}, session)

        return SuccessResponse(
            message="Admin logged out successfully",
        )

    async def refresh_admin_token(self, session: AsyncSession, request: Request):
        refresh_token = request.cookies.get("admin_refresh_token")

        if not refresh_token:
            refresh_token = request.headers.get("admin_refresh_token")

        if not refresh_token:
            return ErrorResponse(message="Refresh token not found", status_code=401)

        curr_admin = self.admin_auth_service.get_current_admin(refresh_token)

        admin = await self.admin_service.get_admin(session=session, admin_id=curr_admin.id)

        if not admin or admin.refresh_token != refresh_token:
            return ErrorResponse(message="Invalid refresh token", status_code=401)

        await self.admin_service.update_admin(admin.id, {"refresh_token": None}, session)

        if admin.id is None:
            return ErrorResponse(message="Admin not found", status_code=404)

        payload = TokenPayload(
            id=admin.id,
            email=admin.email,
            role=admin.role,
        )

        access_token, access_expiry = self.admin_auth_service.create_access_token(payload, 300)
        refresh_token, _ = self.admin_auth_service.create_refresh_token(payload, 3600)

        if admin.id is not None:
            await self.admin_service.update_admin(
                admin.id, {"refresh_token": refresh_token}, session
            )

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
                    "refresh_token": refresh_token,
                },
            },
            status_code=200,
        )
