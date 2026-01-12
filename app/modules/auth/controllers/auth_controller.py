import secrets
from datetime import datetime, timedelta, timezone
from pathlib import Path

from fastapi import BackgroundTasks, Request
from sqlmodel.ext.asyncio.session import AsyncSession

from app.common.lib.formatter import ErrorResponse, SuccessResponse, TokenPayload
from app.config.settings import settings
from app.modules.auth.schemas.auth_validations import Login, Signup
from app.modules.auth.services.auth_service import AuthService
from app.modules.common.services.email_service import email_service
from app.modules.users.services.user_service import UserService


class AuthController:
    def __init__(self):
        self.auth_service = AuthService()
        self.user_service = UserService()

    async def signup(self, data: Signup, session: AsyncSession, background_tasks: BackgroundTasks):
        try:
            if data.password != data.confirm_password:
                return ErrorResponse(
                    message="Password and confirm password do not match", status_code=400
                )

            # Check if user already exists by email or username
            existing_user_by_email = await self.user_service.get_user(session, email=data.email)
            if existing_user_by_email:
                return ErrorResponse(message="Email already registered", status_code=400)

            existing_user_by_username = await self.user_service.get_user(
                session, username=data.username
            )
            if existing_user_by_username:
                return ErrorResponse(message="Username already taken", status_code=400)

            # Create new user
            hashed_password = self.auth_service.hash_password(data.password)
            user_data = {
                "first_name": data.first_name,
                "last_name": data.last_name,
                "email": data.email,
                "password": hashed_password,
                "username": data.username,
            }
            new_user = await self.user_service.create_user(user_data, session)

            if new_user is None or new_user.id is None:
                await session.rollback()
                return ErrorResponse(message="Failed to create user", status_code=500)

            # Generate verification token
            verification_token = secrets.token_urlsafe(32)
            verification_expires = datetime.now(timezone.utc) + timedelta(hours=24)

            # Store verification token
            await self.user_service.update_user(
                new_user.id,
                {
                    "verification_token": verification_token,
                    "verification_token_expires": verification_expires,
                },
                session,
            )

            # Send verification email
            template_path = Path("app/modules/common/email-templates/verify-email.html")
            if not template_path.exists():
                await session.rollback()
                return ErrorResponse(message="Email template not found", status_code=500)

            template_content = template_path.read_text(encoding="utf-8")

            verification_link: str = (
                f"{settings.USER_APP_URL}/verify-email?token={verification_token}"
            )

            html_content = template_content.replace(
                "{{name}}", f"{new_user.first_name} {new_user.last_name}"
            )
            html_content = html_content.replace("{{verify_link}}", verification_link)

            background_tasks.add_task(
                email_service.send_mail,
                recievers_list=[new_user.email],
                subject="Verify your email - Algorithmic Dev",
                html=html_content,
            )

            # Commit the transaction only after all operations succeed
            await session.commit()

            return SuccessResponse(
                message="User created successfully. Please verify your email.",
                data={
                    "user_id": new_user.id,
                    "email": new_user.email,
                    "role": new_user.role,
                    "message": "Verification token has been sent to your email.",
                },
                status_code=201,
            )
        except Exception as e:
            await session.rollback()
            return ErrorResponse(message="Signup failed", error=e, status_code=500)

    async def login(self, data: Login, session: AsyncSession):
        user = None
        if data.email:
            user = await self.user_service.get_user(session, email=data.email)
        if data.username:
            user = await self.user_service.get_user(session, username=data.username)

        if not user:
            return ErrorResponse(message="User not found", status_code=404)

        if not self.auth_service.verify_password(data.password, user.password):
            return ErrorResponse(message="Invalid credentials", status_code=400)

        # Check email verification
        if not user.email_verified:
            return ErrorResponse(
                message="Email not verified. Please verify your email before logging in.",
                status_code=400,
            )

        if user.id is None:
            return ErrorResponse(message="User ID is missing", status_code=400)

        payload: TokenPayload = TokenPayload(id=user.id, email=user.email, role=user.role)

        access_token, access_expiry = self.auth_service.create_access_token(payload)
        refresh_token, refresh_expiry = self.auth_service.create_refresh_token(payload)

        if user.id is not None:
            await self.user_service.update_user(user.id, {"refresh_token": refresh_token}, session)

        # Create response object
        return SuccessResponse(
            message="Login successful",
            data={
                "user": {
                    "id": user.id,
                    "email": user.email,
                    "role": user.role,
                },
                "tokens": {
                    "access_token": access_token,
                    "expires_in": access_expiry,
                    "refresh_token": refresh_token,
                },
            },
            status_code=200,
        )

    async def logout(self, session: AsyncSession, current_user: TokenPayload):
        user = await self.user_service.get_user(session, user_id=current_user.id)
        if not user:
            return ErrorResponse(message="User not found", status_code=404)

        if user.id is not None:
            await self.user_service.update_user(user.id, {"refresh_token": None}, session)

        # Create response object
        return SuccessResponse(
            message="Logout successful",
        )

    async def verify_email(self, token: str, session: AsyncSession):
        """Verify user email using verification token"""
        # Find user with this verification token
        user = await self.user_service.get_user(session, verification_token=token)

        if not user:
            return ErrorResponse(message="Invalid verification token", status_code=400)

        # Check if token has expired
        # Check if token has expired
        verification_expires = user.verification_token_expires
        if verification_expires:
            if isinstance(verification_expires, str):
                try:
                    verification_expires = datetime.fromisoformat(verification_expires)
                except ValueError:
                    # Try parsing if it didn't match isoformat exactly or has specific format
                    # But if it fails, we might just assume expired or log error
                    return ErrorResponse(message="Invalid token expiration format", status_code=500)

            # Ensure timezone awareness for comparison
            if verification_expires.tzinfo is None:
                verification_expires = verification_expires.replace(tzinfo=timezone.utc)

            if verification_expires < datetime.now(timezone.utc):
                return ErrorResponse(message="Verification token has expired", status_code=400)

        # Mark email as verified and clear verification token
        if user.id is not None:
            await self.user_service.update_user(
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

    async def refresh(self, session: AsyncSession, request: Request):
        """Refresh access and refresh tokens using a valid refresh token"""

        # Check cookies first, then fall back to headers
        refresh_token = request.cookies.get("refresh_token")
        if not refresh_token:
            refresh_token = request.headers.get("refresh_token")

        if not refresh_token:
            return ErrorResponse(message="Refresh token is missing", status_code=400)

        curr_user = self.auth_service.get_current_user(refresh_token)

        # Check if refresh token is expired
        if curr_user.exp is not None and datetime.fromtimestamp(curr_user.exp) < datetime.now():
            return ErrorResponse(message="Refresh token has expired", status_code=401)

        # Get user from database
        user = await self.user_service.get_user(session=session, user_id=curr_user.id)

        # Validate refresh token
        if not user or user.refresh_token is None:
            return ErrorResponse(message="Invalid refresh token", status_code=401)

        # Check if the provided refresh token matches the one in the database
        if user.refresh_token != refresh_token:
            return ErrorResponse(message="Refresh token does not match", status_code=401)

        # TOKEN ROTATION: Invalidate old refresh token immediately
        # This prevents token replay attacks
        await self.user_service.update_user(user.id, {"refresh_token": None}, session)

        # Ensure user ID is present
        if user.id is None:
            return ErrorResponse(message="User ID is missing", status_code=400)

        payload: TokenPayload = TokenPayload(id=user.id, email=user.email, role=user.role)

        # Create new tokens
        access_token, access_expiry = self.auth_service.create_access_token(payload)
        refresh_token, refresh_expiry = self.auth_service.create_refresh_token(payload)

        # Update refresh token in database
        await self.user_service.update_user(user.id, {"refresh_token": refresh_token}, session)

        # Create response object
        return SuccessResponse(
            message="Token refreshed successfully",
            data={
                "user": {
                    "id": user.id,
                    "email": user.email,
                    "role": user.role,
                },
                "tokens": {
                    "access_token": access_token,
                    "expires_in": access_expiry,
                    "refresh_token": refresh_token,
                },
            },
            status_code=200,
        )
