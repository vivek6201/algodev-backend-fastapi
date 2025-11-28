from fastapi.param_functions import Depends
from jose.exceptions import JWTError

from app.common.lib.formatter import TokenPayload
from app.modules.auth.services.auth_service import AuthService, OAuth2PasswordBearerWithCookie

oauth_scheme = OAuth2PasswordBearerWithCookie(tokenUrl="/api/auth/admin/login")


class AdminAuthService(AuthService):
    def get_current_admin(self, token: str = Depends(oauth_scheme)) -> TokenPayload:
        payload = self.verify_token(token)

        if payload is None:
            raise JWTError("Could not validate credentials")

        return TokenPayload(**payload)
