from app.db.config import get_session
from fastapi import APIRouter, Depends
from app.controllers.auth_controller import AuthController
from app.validations.auth_validations import Login, Signup
from sqlmodel import Session
from app.common.formatter import TokenPayload

auth_router = APIRouter()
auth_controller = AuthController()


@auth_router.post("/login")
async def login(body: Login, session: Session = Depends(get_session)):
    return await auth_controller.login(body, session)


@auth_router.post("/signup")
async def signup(body: Signup, session: Session = Depends(get_session)):
    return await auth_controller.signup(body, session)


@auth_router.post("/refresh-token")
async def refresh_token():
    pass


@auth_router.post("/logout/{user_id}")
async def logout(user_id: int, session: Session = Depends(get_session), current_user: TokenPayload = Depends(auth_controller.auth_service.get_current_user)):
    return await auth_controller.logout(user_id=user_id, session=session, current_user=current_user)
