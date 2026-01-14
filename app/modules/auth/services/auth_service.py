from datetime import datetime, timedelta, timezone
from typing import Optional

from bcrypt import checkpw, gensalt, hashpw
from fastapi import Depends, HTTPException, Request
from fastapi.security import OAuth2PasswordBearer
from jose import ExpiredSignatureError, JWTError, jwt

from app.common.lib.formatter import TokenPayload
from app.config.settings import settings


class OAuth2PasswordBearerWithCookie(OAuth2PasswordBearer):
    """Custom OAuth2 scheme that checks cookies first, then falls back to Authorization header"""

    async def __call__(self, request: Request) -> Optional[str]:
        # Check cookie first
        token = request.cookies.get("access_token")
        if token:
            return token

        # Fall back to Authorization header
        return await super().__call__(request)


class OptionalOAuth2PasswordBearerWithCookie(OAuth2PasswordBearer):
    """Optional OAuth2 scheme that checks cookies first, returns None if no token found"""

    async def __call__(self, request: Request) -> Optional[str]:
        # Check cookie first
        token = request.cookies.get("access_token")
        if token:
            return token

        # Fall back to Authorization header
        try:
            return await super().__call__(request)
        except HTTPException:
            return None


oauth_scheme = OAuth2PasswordBearerWithCookie(tokenUrl="/api/auth/login")

# Optional OAuth scheme for public endpoints that work with or without authentication
optional_oauth_scheme = OptionalOAuth2PasswordBearerWithCookie(
    tokenUrl="/api/auth/login", auto_error=False
)


class AuthService:
    def __init__(self):
        self.settings = settings

    def get_current_user(self, token: str = Depends(oauth_scheme)) -> TokenPayload:
        payload = self.verify_token(token)

        if payload is None:
            raise JWTError("Could not validate credentials")

        return TokenPayload(**payload)

    def validate_role(self, token: str = Depends(oauth_scheme), allowed_roles: list = []):
        payload = self.get_current_user(token)
        if payload.role not in allowed_roles:
            return False
        return True

    def create_access_token(
        self, data: TokenPayload, expires_delta: Optional[timedelta | int] = None
    ) -> tuple[str, datetime]:
        to_encode = data.__dict__.copy()
        if expires_delta:
            if isinstance(expires_delta, int):
                expires_delta = timedelta(seconds=expires_delta)
            expire = datetime.now(timezone.utc) + expires_delta
        else:
            expire = datetime.now(timezone.utc) + timedelta(
                seconds=self.settings.ACCESS_TOKEN_EXPIRE_SECONDS
            )
        to_encode.update({"exp": expire})
        encoded_jwt = jwt.encode(
            to_encode, self.settings.SECRET_KEY, algorithm=self.settings.ALGORITHM
        )
        return encoded_jwt, expire

    def create_refresh_token(
        self, data: TokenPayload, expires_delta: Optional[timedelta | int] = None
    ) -> tuple[str, datetime]:
        to_encode = data.__dict__.copy()
        if expires_delta:
            if isinstance(expires_delta, int):
                expires_delta = timedelta(seconds=expires_delta)
            expire = datetime.now(timezone.utc) + expires_delta
        else:
            expire = datetime.now(timezone.utc) + timedelta(
                seconds=self.settings.REFRESH_TOKEN_EXPIRE_SECONDS
            )
        to_encode.update({"exp": expire})
        encoded_jwt = jwt.encode(
            to_encode, self.settings.SECRET_KEY, algorithm=self.settings.ALGORITHM
        )

        return encoded_jwt, expire

    def verify_token(self, token: str):
        try:
            payload = jwt.decode(
                token, self.settings.SECRET_KEY, algorithms=[self.settings.ALGORITHM]
            )
            return payload
        except ExpiredSignatureError:
            raise HTTPException(status_code=401, detail="Token has expired")
        except JWTError:
            raise HTTPException(status_code=401, detail="Could not validate credentials")

    def hash_password(self, password: str) -> str:
        return hashpw(password.encode("utf-8"), gensalt()).decode("utf-8")

    def verify_password(self, plain_password: str, hashed_password: str) -> bool:
        return checkpw(plain_password.encode("utf-8"), hashed_password.encode("utf-8"))
