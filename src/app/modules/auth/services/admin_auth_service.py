from fastapi.param_functions import Depends

from app.common.lib.formatter import TokenPayload
from app.modules.auth.services.auth_service import AuthService, OAuth2PasswordBearerWithCookie

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
