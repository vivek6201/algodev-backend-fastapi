from fastapi import Request
from sqlmodel import Session, select

from app.common.lib.formatter import ErrorResponse, SuccessResponse, TokenPayload
from app.config.settings import settings
from app.modules.auth.schemas.auth_validations import AdminLogin
from app.modules.auth.services.admin_auth_service import AdminAuthService
from app.modules.users.models.admin import Admin
from app.modules.users.services.admin_service import AdminService


class AdminAuthController:
    def __init__(self):
        self.admin_auth_service = AdminAuthService()
        self.admin_service = AdminService()

    def admin_login(
        self,
        body: AdminLogin,
        session: Session,
    ):
        try:
            admin = session.exec(select(Admin).where(Admin.email == body.email)).one_or_none()
        except Exception as e:
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

        access_token = self.admin_auth_service.create_access_token(payload)
        refresh_token = self.admin_auth_service.create_refresh_token(payload)

        if admin.id is not None:
            self.admin_service.update_admin(admin.id, {"refresh_token": refresh_token}, session)

        # Create response object
        response = SuccessResponse(
            message="Admin logged in successfully",
            data={
                "id": admin.id,
                "email": admin.email,
                "role": admin.role,
            },
            status_code=200,
        )

        # Set tokens in HTTP-only cookies
        response.set_cookie(
            key="access_token",
            value=access_token,
            httponly=True,
            max_age=3600,
            path="/",
            samesite="lax",
            domain=settings.DOMAIN,
        )
        response.set_cookie(
            key="refresh_token",
            value=refresh_token,
            httponly=True,
            max_age=60 * 60 * 24,
            path="/",
            samesite="lax",
            domain=settings.DOMAIN,
        )

        return response

    def admin_logout(self, session: Session, current_admin: TokenPayload):
        admin = self.admin_service.get_admin(admin_id=current_admin.id, session=session)

        if not admin:
            return ErrorResponse(message="Admin not found", status_code=404)

        if admin.id is not None:
            self.admin_service.update_admin(admin.id, {"refresh_token": None}, session)

        # Create response object
        response = SuccessResponse(
            message="Admin logged out successfully",
        )

        # Clear cookies
        response.delete_cookie(key="access_token")
        response.delete_cookie(key="refresh_token")

        return response

    def refresh_admin_token(self, session: Session, request: Request):
        refresh_token = request.cookies.get("refresh_token")

        if not refresh_token:
            refresh_token = request.headers.get("refresh_token")

        if not refresh_token:
            return ErrorResponse(message="Refresh token not found", status_code=401)

        curr_admin = self.admin_auth_service.get_current_admin(refresh_token)

        admin = self.admin_service.get_admin(session=session, admin_id=curr_admin.id)

        if not admin or admin.refresh_token != refresh_token:
            return ErrorResponse(message="Invalid refresh token", status_code=401)

        self.admin_service.update_admin(admin.id, {"refresh_token": None}, session)

        if admin.id is None:
            return ErrorResponse(message="Admin not found", status_code=404)

        payload = TokenPayload(
            id=admin.id,
            email=admin.email,
            role=admin.role,
        )

        access_token = self.admin_auth_service.create_access_token(payload)
        refresh_token = self.admin_auth_service.create_refresh_token(payload)

        if admin.id is not None:
            self.admin_service.update_admin(admin.id, {"refresh_token": refresh_token}, session)

        response = SuccessResponse(
            message="Token refreshed successfully",
            data={
                "id": admin.id,
                "email": admin.email,
                "role": admin.role,
            },
            status_code=200,
        )

        # Set tokens in HTTP-only cookies
        response.set_cookie(
            key="access_token",
            value=access_token,
            httponly=True,
            max_age=3600,
            path="/",
            samesite="lax",
            domain=settings.DOMAIN,
        )

        response.set_cookie(
            key="refresh_token",
            value=refresh_token,
            httponly=True,
            max_age=60 * 60 * 24,
            path="/",
            samesite="lax",
            domain=settings.DOMAIN,
        )

        return response
