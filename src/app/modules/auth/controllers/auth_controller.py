
from app.modules.auth.services.auth_service import AuthService
from app.modules.users.services.user_service import UserService
from app.modules.auth.schemas.auth_validations import Login, Signup
from sqlmodel import Session
from app.common.lib.formatter import SuccessResponse, ErrorResponse
from app.common.lib.formatter import TokenPayload
from datetime import datetime
from fastapi import Request

class AuthController:
    def __init__(self):
        self.auth_service = AuthService()
        self.user_service = UserService()

    def signup(self, data: Signup, session: Session):
        if data.password != data.confirm_password:
            return ErrorResponse(
                message="Password and confirm password do not match",
                status_code=400
            )

        user = self.user_service.get_user(session, email=data.email)

        if not user:
            user = self.user_service.get_user(session, username=data.username)

        if user:
            return ErrorResponse(
                message="User with this email or username already exists",
                status_code=400,
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
                status_code=400
            )

        payload: TokenPayload = TokenPayload(
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
            },
            status_code=201
        )

    def login(self, data: Login, session: Session):
        user = None
        if data.email:
            user = self.user_service.get_user(session, email=data.email)
        if data.username:
            user = self.user_service.get_user(session, username=data.username)

        if not user:
            return ErrorResponse(
                message="User not found",
                status_code=404
            )

        if not self.auth_service.verify_password(data.password, user.password):
            return ErrorResponse(
                message="Invalid credentials",
                status_code=400
            )

        if user.id is None:
            return ErrorResponse(
                message="User ID is missing",
                status_code=400
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
            },
            status_code=200
        )

    def logout(self, user_id: int, session: Session, current_user: TokenPayload):
        if current_user.id != user_id:
            return ErrorResponse(
                message="Unauthorized to logout this user",
                status_code=400
            )

        user = self.user_service.get_user(session, user_id=user_id)
        if not user:
            return ErrorResponse(
                message="User not found",
                status_code=404
            )

        if user.id is not None:
            self.user_service.update_user(user.id, {
                "refresh_token": None
            }, session)

        return SuccessResponse(
            message="Logout successful",
        )

    def refresh(self, session: Session, request: Request):
        '''Refresh access and refresh tokens using a valid refresh token'''
        
        # check whether it comes in headers or cookies (V.V.IMP)
        refresh_token = request.headers.get("refresh_token")
        if not refresh_token:
            return ErrorResponse(
                message="Refresh token is missing",
                status_code=400
            )
        
        curr_user = self.auth_service.get_current_user(refresh_token)  
        
        # Check if refresh token is expired
        if curr_user.exp is not None and datetime.fromtimestamp(curr_user.exp) < datetime.now():
            return ErrorResponse(
                message="Refresh token has expired",
                status_code=401
            )

        # Get user from database
        user = self.user_service.get_user(
            session=session, user_id=curr_user.id)

        # Validate refresh token
        if not user or user.refresh_token is None:
            return ErrorResponse(
                message="Invalid refresh token",
                status_code=401
            )
            
        # Check if the provided refresh token matches the one in the database
        if user.refresh_token != refresh_token:
            return ErrorResponse(
                message="Refresh token does not match",
                status_code=401
            )

        # Ensure user ID is present
        if user.id is None:
            return ErrorResponse(
                message="User ID is missing",
                status_code=400
            )

        payload: TokenPayload = TokenPayload(
            id=user.id,
            email=user.email,
            role=user.role
        )
        
        # Create new tokens
        access_token = self.auth_service.create_access_token(payload)
        refresh_token = self.auth_service.create_refresh_token(payload)

        # Update refresh token in database
        self.user_service.update_user(user.id, {
            "refresh_token": refresh_token
        }, session)

        # Return new tokens
        return SuccessResponse(
            message="Token refreshed successfully",
            data={
                "access_token": access_token,
                "refresh_token": refresh_token,
            },
            status_code=200
        )
