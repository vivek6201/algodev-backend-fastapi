from fastapi import APIRouter, Depends
from sqlmodel import Session

from app.common.db.config import get_session
from app.modules.education.shared.controllers.base_controller import BaseEducationController
from app.modules.education.shared.model import EducationCategory

edu_router = APIRouter()
base_controller = BaseEducationController()


@edu_router.get("/categories", response_model=list[EducationCategory])
def get_categories(session: Session = Depends(get_session)):
    return base_controller.get_categories(session=session)
