
from ..services.auth_service import AuthService
from ..services.user_service import UserService
from ..validations.auth_validations import Login, Signup
from sqlmodel import Session
from ..common.formatter import SuccessResponse, ErrorResponse
from ..common.formatter import TokenPayload

class AuthController:
    def __init__(self):
        self.auth_service = AuthService()
        self.user_service = UserService()

    async def signup(self, data: Signup, session: Session):
        if data.password != data.confirm_password:
            return ErrorResponse(
                message="Password and confirm password do not match",
            )
        
        user = self.user_service.get_user(session, email=data.email)
        
        if not user:
            user = self.user_service.get_user(session, username=data.username)
        
        if user:
            return ErrorResponse(
                message="User with this email or username already exists",
            )
        
        hashed_password = self.auth_service.hash_password(data.password)
        user_data = {
            "first_name": data.first_name,
            "last_name": data.last_name,
            "email": data.email,
            "password": hashed_password,
            "username": data.username
        }
        
        new_user = self.user_service.create_user(user_data, session)
        
        if new_user.id is None:
            return ErrorResponse(
                message="Failed to create user: missing user ID",
            )

        payload:TokenPayload = TokenPayload(
            id=new_user.id,
            email=new_user.email,
            role=new_user.role
        )
        
        access_token = self.auth_service.create_access_token(payload)
        refresh_token = self.auth_service.create_refresh_token(payload)
        
        self.user_service.update_user(new_user.id, {
            "refresh_token": refresh_token
        }, session)
        
        return SuccessResponse(
            message="User created successfully",
            data={
                "access_token": access_token,
                "refresh_token": refresh_token,
            }
        )

    async def login(self, data: Login, session: Session):
        user = None
        if data.email:
            user = self.user_service.get_user(session, email=data.email)
        if data.username:
            user = self.user_service.get_user(session, username=data.username)
            
        if not user:
            return ErrorResponse(
                message="User not found",
            )
            
        
        if not self.auth_service.verify_password(data.password, user.password):
            return ErrorResponse(
                message="Invalid credentials",
            )
            
        if user.id is None:
            return ErrorResponse(
                message="User ID is missing",
            )
        
        payload: TokenPayload = TokenPayload(
            id=user.id,
            email=user.email,
            role=user.role
        )
        
        access_token = self.auth_service.create_access_token(payload)
        refresh_token = self.auth_service.create_refresh_token(payload)
        
        if user.id is not None:
            self.user_service.update_user(user.id, {
                "refresh_token": refresh_token
            }, session)
        
        return SuccessResponse(
            message="Login successful",
            data={
                "access_token": access_token,
                "refresh_token": refresh_token,
            }
        )
        
    async def logout(self, user_id: int, session: Session, current_user: TokenPayload):
        if current_user.id != user_id:
            return ErrorResponse(
                message="Unauthorized to logout this user",
            )
        
        user = self.user_service.get_user(session, user_id=user_id)
        if not user:
            return ErrorResponse(
                message="User not found",
            )
        
        if user.id is not None:
            self.user_service.update_user(user.id, {
                "refresh_token": None
            }, session)
        
        return SuccessResponse(
            message="Logout successful",
        )