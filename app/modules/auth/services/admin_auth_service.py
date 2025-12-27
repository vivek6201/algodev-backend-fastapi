from typing import Optional

from fastapi import Request
from fastapi.param_functions import Depends
from fastapi.security import OAuth2PasswordBearer

from app.common.lib.formatter import TokenPayload
from app.modules.auth.services.auth_service import AuthService


class OAuth2PasswordBearerWithCookie(OAuth2PasswordBearer):
    """Custom OAuth2 scheme that checks cookies first, then falls back to Authorization header"""

    async def __call__(self, request: Request) -> Optional[str]:
        # Check cookie first
        token = request.cookies.get("admin_access_token")
        if token:
            return token

        # Fall back to Authorization header
        return await super().__call__(request)


oauth_scheme = OAuth2PasswordBearerWithCookie(tokenUrl="/api/auth/admin/login")


class AdminAuthService(AuthService):
    def get_current_admin(self, token: str = Depends(oauth_scheme)) -> TokenPayload:
        payload = self.verify_token(token)
        return TokenPayload(**payload)

    def validate_role(self, token: str = Depends(oauth_scheme), allowed_roles: list = []):
        payload = self.get_current_admin(token)

        if payload.role not in allowed_roles:
            return False
        return True
