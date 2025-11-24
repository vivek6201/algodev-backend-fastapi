from datetime import datetime, timedelta

from fastapi import Request
from sqlmodel import Session

from app.common.lib.formatter import ErrorResponse, SuccessResponse, TokenPayload
from app.modules.auth.schemas.auth_validations import Login, Signup
from app.modules.auth.services.auth_service import AuthService
from app.modules.users.services.user_service import UserService


class AuthController:
    def __init__(self):
        self.auth_service = AuthService()
        self.user_service = UserService()

    def signup(self, data: Signup, session: Session):
        if data.password != data.confirm_password:
            return ErrorResponse(
                message="Password and confirm password do not match", status_code=400
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
            "username": data.username,
        }

        new_user = self.user_service.create_user(user_data, session)

        if new_user.id is None:
            return ErrorResponse(message="Failed to create user: missing user ID", status_code=400)

        # Generate verification token
        verification_token = self.auth_service.generate_verification_token()
        verification_expires = datetime.now() + timedelta(hours=24)

        # Update user with verification token
        self.user_service.update_user(
            new_user.id,
            {
                "verification_token": verification_token,
                "verification_token_expires": verification_expires,
            },
            session,
        )

        # TODO: Send verification email
        # For now, log the token
        print(f"\n{'=' * 60}")
        print(f"EMAIL VERIFICATION for {new_user.email}")
        print(f"{'=' * 60}")
        print(f"Click this link to verify your email:")
        print(f"  http://localhost:4001/api/auth/verify-email/{verification_token}")
        print(f"Token expires: {verification_expires}")
        print(f"{'=' * 60}\n")

        return SuccessResponse(
            message="User created successfully. Please verify your email.",
            data={
                "user_id": new_user.id,
                "email": new_user.email,
                "role": new_user.role,
                "message": "Verification token has been logged to console (check server logs)",
            },
            status_code=201,
        )

    def login(self, data: Login, session: Session):
        user = None
        if data.email:
            user = self.user_service.get_user(session, email=data.email)
        if data.username:
            user = self.user_service.get_user(session, username=data.username)

        if not user:
            return ErrorResponse(message="User not found", status_code=404)

        if not self.auth_service.verify_password(data.password, user.password):
            return ErrorResponse(message="Invalid credentials", status_code=400)

        # Check email verification
        if not user.email_verified:
            return ErrorResponse(
                message="Email not verified. Please verify your email before logging in.",
                status_code=403,
            )

        if user.id is None:
            return ErrorResponse(message="User ID is missing", status_code=400)

        payload: TokenPayload = TokenPayload(id=user.id, email=user.email, role=user.role)

        access_token = self.auth_service.create_access_token(payload)
        refresh_token = self.auth_service.create_refresh_token(payload)

        if user.id is not None:
            self.user_service.update_user(user.id, {"refresh_token": refresh_token}, session)

        return SuccessResponse(
            message="Login successful",
            data={
                "access_token": access_token,
                "refresh_token": refresh_token,
            },
            status_code=200,
        )

    def logout(self, user_id: int, session: Session, current_user: TokenPayload):
        if current_user.id != user_id:
            return ErrorResponse(message="Unauthorized to logout this user", status_code=400)

        user = self.user_service.get_user(session, user_id=user_id)
        if not user:
            return ErrorResponse(message="User not found", status_code=404)

        if user.id is not None:
            self.user_service.update_user(user.id, {"refresh_token": None}, session)

        return SuccessResponse(
            message="Logout successful",
        )

    def verify_email(self, token: str, session: Session):
        """Verify user email using verification token"""
        # Find user with this verification token
        user = self.user_service.get_user(session, verification_token=token)

        if not user:
            return ErrorResponse(message="Invalid verification token", status_code=400)

        # Check if token has expired
        if user.verification_token_expires and user.verification_token_expires < datetime.now():
            return ErrorResponse(message="Verification token has expired", status_code=400)

        # Mark email as verified and clear verification token
        if user.id is not None:
            self.user_service.update_user(
                user.id,
                {
                    "email_verified": True,
                    "verification_token": None,
                    "verification_token_expires": None,
                },
                session,
            )

        return SuccessResponse(
            message="Email verified successfully. You can now log in.", status_code=200
        )

    def refresh(self, session: Session, request: Request):
        """Refresh access and refresh tokens using a valid refresh token"""

        # check whether it comes in headers or cookies (V.V.IMP)
        refresh_token = request.headers.get("refresh_token")
        if not refresh_token:
            return ErrorResponse(message="Refresh token is missing", status_code=400)

        curr_user = self.auth_service.get_current_user(refresh_token)

        # Check if refresh token is expired
        if curr_user.exp is not None and datetime.fromtimestamp(curr_user.exp) < datetime.now():
            return ErrorResponse(message="Refresh token has expired", status_code=401)

        # Get user from database
        user = self.user_service.get_user(session=session, user_id=curr_user.id)

        # Validate refresh token
        if not user or user.refresh_token is None:
            return ErrorResponse(message="Invalid refresh token", status_code=401)

        # Check if the provided refresh token matches the one in the database
        if user.refresh_token != refresh_token:
            return ErrorResponse(message="Refresh token does not match", status_code=401)

        # TOKEN ROTATION: Invalidate old refresh token immediately
        # This prevents token replay attacks
        self.user_service.update_user(user.id, {"refresh_token": None}, session)

        # Ensure user ID is present
        if user.id is None:
            return ErrorResponse(message="User ID is missing", status_code=400)

        payload: TokenPayload = TokenPayload(id=user.id, email=user.email, role=user.role)

        # Create new tokens
        access_token = self.auth_service.create_access_token(payload)
        refresh_token = self.auth_service.create_refresh_token(payload)

        # Update refresh token in database
        self.user_service.update_user(user.id, {"refresh_token": refresh_token}, session)

        # Return new tokens
        return SuccessResponse(
            message="Token refreshed successfully",
            data={
                "access_token": access_token,
                "refresh_token": refresh_token,
            },
            status_code=200,
        )
