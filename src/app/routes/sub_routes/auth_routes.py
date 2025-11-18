from app.db.config import get_session
from fastapi import APIRouter, Depends
from app.controllers.auth_controller import AuthController
from app.validations.auth_validations import Login, Signup
from sqlmodel import Session

auth_router = APIRouter()

auth_controller = AuthController()

@auth_router.post("/login")
async def login(body: Login, session: Session = Depends(get_session)):
    return await auth_controller.login(body, session)

@auth_router.post("/signup")
async def signup(body: Signup, session: Session = Depends(get_session)):
    return await auth_controller.signup(body, session)