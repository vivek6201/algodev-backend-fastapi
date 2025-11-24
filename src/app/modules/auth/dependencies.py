from typing import Optional

from fastapi import Depends, HTTPException, status

from app.common.lib.formatter import TokenPayload
from app.modules.auth.services.auth_service import AuthService, oauth_scheme, optional_oauth_scheme

ALL_ROLES = ["ADMIN", "USER", "MODERATOR", "GUEST", "RECRUITER"]


class RoleChecker:
    def __init__(self, allowed_roles: list[str]):
        self.allowed_roles = allowed_roles

    def __call__(self, token: str = Depends(oauth_scheme)):
        auth_service = AuthService()

        if not auth_service.validate_role(token, self.allowed_roles):
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN, detail="Operation not permitted"
            )

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
