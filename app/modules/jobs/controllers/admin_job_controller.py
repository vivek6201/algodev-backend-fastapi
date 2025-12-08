from sqlmodel import Session

from app.common.lib.formatter import ErrorResponse, SuccessResponse, TokenPayload
from app.modules.jobs.controllers.job_controller import JobController
from app.modules.jobs.schemas.category_validations import CategoryCreate, CategoryUpdate
from app.modules.jobs.schemas.job_validations import (
    JobResponse,
    ThirdPartyJobCreate,
    ThirdPartyJobUpdate,
)
from app.modules.jobs.services.admin_job_service import AdminJobService
from app.modules.users.models.admin import Admin


class AdminJobController(JobController):
    def __init__(self):
        self.job_service = AdminJobService()

    def create_category(
        self,
        session: Session,
        category_data: CategoryCreate,
        current_admin: TokenPayload,
    ):
        admin = session.get(Admin, current_admin.id)
        if not admin:
            return ErrorResponse(message="Admin not found", status_code=404)

        new_category = self.job_service.create_category(session, category_data)

        if not new_category:
            return ErrorResponse(message="Category with this name already exists", status_code=400)

        return SuccessResponse(
            message="Category created successfully", data=new_category, status_code=201
        )

    def update_category(
        self,
        session: Session,
        category_id: int,
        category_data: CategoryUpdate,
        current_admin: TokenPayload,
    ):
        admin = session.get(Admin, current_admin.id)
        if not admin:
            return ErrorResponse(message="Admin not found", status_code=404)

        updated_category = self.job_service.update_category(
            session, category_id, category_data, admin
        )

        if not updated_category:
            return ErrorResponse(message="Category not found", status_code=404)

        return SuccessResponse(
            message="Category updated successfully", data=updated_category, status_code=200
        )

    def create_job(
        self,
        session: Session,
        job_data: ThirdPartyJobCreate,
        current_admin: TokenPayload,
    ):
        admin = session.get(Admin, current_admin.id)
        if not admin:
            return ErrorResponse(message="Admin not found", status_code=404)

        new_job = self.job_service.create_job(session, job_data, admin)

        if not new_job:
            return ErrorResponse(message="Job with this title already exists", status_code=400)

        return SuccessResponse(message="Job created successfully", data=new_job, status_code=201)

    def update_job(
        self,
        session: Session,
        job_slug: str,
        job_data: ThirdPartyJobUpdate,
        current_admin: TokenPayload,
    ):
        admin = session.get(Admin, current_admin.id)
        if not admin:
            return ErrorResponse(message="Admin not found", status_code=404)

        updated_job = self.job_service.update_job(session, job_slug, job_data)

        if not updated_job:
            return ErrorResponse(message="Job not found", status_code=404)

        updated_job = JobResponse.model_validate(updated_job)

        return SuccessResponse(
            message="Job updated successfully", data=updated_job, status_code=200
        )
