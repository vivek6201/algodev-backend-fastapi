from fastapi import Depends
from fastapi.routing import APIRouter
from sqlmodel import Session

from app.common.db.config import get_session
from app.common.lib.formatter import TokenPayload
from app.modules.auth.dependencies import ALL_ADMIN_ROLES, RoleChecker
from app.modules.jobs.controllers.admin_job_controller import AdminJobController
from app.modules.jobs.schemas.category_validations import CategoryCreate, CategoryUpdate
from app.modules.jobs.schemas.job_validations import ThirdPartyJobCreate, ThirdPartyJobUpdate

job_controller = AdminJobController()

admin_job_router = APIRouter()


@admin_job_router.post("/category")
def create_category(
    category_data: CategoryCreate,
    session: Session = Depends(get_session),
    current_admin: TokenPayload = Depends(
        RoleChecker(allowed_roles=ALL_ADMIN_ROLES, user_type="admin")
    ),
):
    return job_controller.create_category(session, category_data, current_admin)


@admin_job_router.patch("/category")
def update_category(
    category_id: int,
    category_data: CategoryUpdate,
    session: Session = Depends(get_session),
    current_admin: TokenPayload = Depends(
        RoleChecker(allowed_roles=ALL_ADMIN_ROLES, user_type="admin")
    ),
):
    return job_controller.update_category(session, category_id, category_data, current_admin)


@admin_job_router.post("/job")
def create_job(
    job_data: ThirdPartyJobCreate,
    session: Session = Depends(get_session),
    current_admin: TokenPayload = Depends(
        RoleChecker(allowed_roles=ALL_ADMIN_ROLES, user_type="admin")
    ),
):
    return job_controller.create_job(session, job_data, current_admin)


@admin_job_router.patch("/job")
def update_job(
    job_slug: str,
    job_data: ThirdPartyJobUpdate,
    session: Session = Depends(get_session),
    current_admin: TokenPayload = Depends(
        RoleChecker(allowed_roles=ALL_ADMIN_ROLES, user_type="admin")
    ),
):
    return job_controller.update_job(session, job_slug, job_data, current_admin)
