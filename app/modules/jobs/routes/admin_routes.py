from fastapi import Depends, Request
from fastapi.routing import APIRouter
from sqlmodel import Session

from app.common.db.config import get_session
from app.common.lib.formatter import TokenPayload
from app.modules.auth.dependencies import ALL_ADMIN_ROLES, RoleChecker
from app.modules.jobs.controllers.admin_job_controller import AdminJobController
from app.modules.jobs.schemas.category_validations import CategoryCreate, CategoryUpdate
from app.modules.jobs.schemas.job_validations import (
    JobStatusUpdate,
    ThirdPartyJobCreate,
    ThirdPartyJobUpdate,
)

job_controller = AdminJobController()

admin_job_router = APIRouter()


@admin_job_router.get("/")
def list_jobs(
    req: Request,
    session: Session = Depends(get_session),
    current_admin: TokenPayload = Depends(
        RoleChecker(allowed_roles=ALL_ADMIN_ROLES, user_type="admin")
    ),
):
    page = req.query_params.get("page")
    limit = req.query_params.get("limit")

    params = {
        "type": req.query_params.get("type"),
        "page": int(page) if page else 1,
        "limit": int(limit) if limit else 10,
        "search": req.query_params.get("search"),
        "status": req.query_params.get("status"),
    }
    return job_controller.list_jobs(session=session, **params)


@admin_job_router.get("/one/{job_slug}")
def get_job(
    job_slug: str,
    session: Session = Depends(get_session),
    current_admin: TokenPayload = Depends(
        RoleChecker(allowed_roles=ALL_ADMIN_ROLES, user_type="admin")
    ),
):
    return job_controller.get_job(session=session, job_slug=job_slug)


@admin_job_router.post("/category")
def create_category(
    category_data: CategoryCreate,
    session: Session = Depends(get_session),
    current_admin: TokenPayload = Depends(
        RoleChecker(allowed_roles=ALL_ADMIN_ROLES, user_type="admin")
    ),
):
    return job_controller.create_category(
        session=session, category_data=category_data, current_admin=current_admin
    )


@admin_job_router.patch("/category/{category_id}")
def update_category(
    category_id: int,
    category_data: CategoryUpdate,
    session: Session = Depends(get_session),
    current_admin: TokenPayload = Depends(
        RoleChecker(allowed_roles=ALL_ADMIN_ROLES, user_type="admin")
    ),
):
    return job_controller.update_category(
        session=session,
        category_id=category_id,
        category_data=category_data,
        current_admin=current_admin,
    )


@admin_job_router.post("/job_create")
def create_job(
    job_data: ThirdPartyJobCreate,
    session: Session = Depends(get_session),
    current_admin: TokenPayload = Depends(
        RoleChecker(allowed_roles=ALL_ADMIN_ROLES, user_type="admin")
    ),
):
    return job_controller.create_job(
        session=session, job_data=job_data, current_admin=current_admin
    )


@admin_job_router.patch("/job_update/{job_slug}")
def update_job(
    job_slug: str,
    job_data: ThirdPartyJobUpdate,
    session: Session = Depends(get_session),
    current_admin: TokenPayload = Depends(
        RoleChecker(allowed_roles=ALL_ADMIN_ROLES, user_type="admin")
    ),
):
    return job_controller.update_job(
        session=session, job_slug=job_slug, job_data=job_data, current_admin=current_admin
    )


@admin_job_router.patch("/change_status/{job_slug}")
def publish_job(
    job_slug: str,
    status_data: JobStatusUpdate,
    session: Session = Depends(get_session),
    current_admin: TokenPayload = Depends(
        RoleChecker(allowed_roles=ALL_ADMIN_ROLES, user_type="admin")
    ),
):
    return job_controller.update_job_status(
        session=session, job_slug=job_slug, status=status_data.status, current_admin=current_admin
    )
