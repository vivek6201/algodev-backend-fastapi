
from datetime import datetime, timedelta
from typing import Optional
from jose import JWTError, jwt
from bcrypt import hashpw, gensalt, checkpw
from app.config.settings import settings
from ..common.formatter import TokenPayload
from fastapi.security import OAuth2PasswordBearer
from fastapi import Depends

oauth_scheme = OAuth2PasswordBearer(tokenUrl="/api/auth")
class AuthService:
    def __init__(self):
        self.settings = settings

    def get_current_user(self, token: str = Depends(oauth_scheme)) -> TokenPayload:
        payload = self.verify_token(token)
        print(payload)
        
        if payload is None:
            raise JWTError("Could not validate credentials")
        
        return TokenPayload(**payload)

    def create_access_token(self, data: TokenPayload, expires_delta: Optional[timedelta] = None):
        to_encode = data.__dict__.copy()
        expire = datetime.now() + (expires_delta or timedelta(minutes=self.settings.ACCESS_TOKEN_EXPIRE_MINUTES))
        to_encode.update({"exp": expire})
        encoded_jwt = jwt.encode(to_encode, self.settings.SECRET_KEY, algorithm=self.settings.ALGORITHM)
        
        return encoded_jwt

    def create_refresh_token(self, data: TokenPayload, expires_delta: Optional[timedelta] = None):
        to_encode = data.__dict__.copy()
        expire = datetime.now() + (expires_delta or timedelta(days=self.settings.REFRESH_TOKEN_EXPIRE_DAYS))
        to_encode.update({"exp": expire})
        encoded_jwt = jwt.encode(to_encode, self.settings.SECRET_KEY, algorithm=self.settings.ALGORITHM)

        return encoded_jwt

    def verify_token(self, token: str):
        try:
            payload = jwt.decode(token, self.settings.SECRET_KEY, algorithms=[self.settings.ALGORITHM])
            return payload
        except JWTError:
            return None

    def hash_password(self, password: str) -> str:
        return hashpw(password.encode('utf-8'), gensalt()).decode('utf-8')

    def verify_password(self, plain_password: str, hashed_password: str) -> bool:
        return checkpw(plain_password.encode('utf-8'), hashed_password.encode('utf-8'))