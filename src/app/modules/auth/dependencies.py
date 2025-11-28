from typing import Optional

from fastapi import Depends, HTTPException, Request, status

from app.common.lib.formatter import TokenPayload
from app.modules.auth.services.admin_auth_service import AdminAuthService
from app.modules.auth.services.admin_auth_service import oauth_scheme as admin_oauth_scheme
from app.modules.auth.services.auth_service import AuthService, oauth_scheme, optional_oauth_scheme
from app.modules.users.models.admin import AdminRole
from app.modules.users.models.user import Role

ALL_ADMIN_ROLES = [role.value for role in AdminRole]
ALL_USER_ROLES = [role.value for role in Role]


class RoleChecker:
    def __init__(self, allowed_roles: list[str], user_type: str = "user"):
        self.allowed_roles = allowed_roles
        self.user_type = user_type

    async def __call__(self, request: Request):
        if self.user_type == "admin":
            token = await admin_oauth_scheme(request)
            auth_service = AdminAuthService()
        else:
            token = await oauth_scheme(request)
            auth_service = AuthService()

        if not auth_service.validate_role(token, self.allowed_roles):
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN, detail="Operation not permitted"
            )

        if self.user_type == "admin":
            return auth_service.get_current_admin(token)
        return auth_service.get_current_user(token)


def get_optional_user(
    token: Optional[str] = Depends(optional_oauth_scheme),
) -> Optional[TokenPayload]:
    """
    Optional user dependency - returns None if no token provided or if token is invalid.
    Used for public endpoints that should work differently for authenticated users.
    """
    if not token:
        return None

    auth_service = AuthService()

    try:
        return auth_service.get_current_user(token)
    except Exception:
        # If token is invalid, treat as unauthenticated
        return None
