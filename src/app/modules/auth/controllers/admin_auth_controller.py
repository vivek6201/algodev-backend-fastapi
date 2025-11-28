from sqlmodel import Session

from app.common.lib.formatter import ErrorResponse, SuccessResponse, TokenPayload
from app.modules.auth.schemas.auth_validations import AdminLogin
from app.modules.auth.services.admin_auth_service import AdminAuthService
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
        admin = self.admin_service.get_admin(email=body.email, session=session)

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
            secure=True,  # Set to True in production with HTTPS
            samesite="lax",
            max_age=3600,  # 1 hour (adjust based on your token expiry)
        )
        response.set_cookie(
            key="refresh_token",
            value=refresh_token,
            httponly=True,
            secure=True,  # Set to True in production with HTTPS
            samesite="lax",
            max_age=604800,  # 7 days (adjust based on your token expiry)
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
