from fastapi import APIRouter, Depends, Query
from app.modules.jobs.controllers.jobs_controller import JobsController
from app.common.db.config import get_session
from sqlmodel import Session
from app.modules.auth.controllers.auth_controller import AuthController
from app.common.lib.formatter import TokenPayload
from app.modules.jobs.schemas.job_validations import ThirdPartyJobCreate, ThirdPartyJobUpdate
from app.modules.jobs.schemas.category_validations import CategoryCreate, CategoryUpdate
from app.modules.auth.dependencies import RoleChecker, get_optional_user
from app.modules.jobs.models.jobs import ListingType

job_controller = JobsController()
auth_controller = AuthController()

jobs_router = APIRouter()

@jobs_router.get("/all")
def list_jobs(
    session: Session = Depends(get_session),
    listing_type: ListingType | None = Query(None, description="Filter by listing type (ThirdParty or Direct)"),
    current_user: TokenPayload | None = Depends(get_optional_user)
):
    return job_controller.list_jobs(session, listing_type, current_user)

@jobs_router.get("/external/{job_id}")
def get_job(
    job_id: int,
    session: Session = Depends(get_session),
    current_user: TokenPayload | None = Depends(get_optional_user)
):
    return job_controller.get_job(session, job_id, listing_type=ListingType.ThirdParty, current_user=current_user)

@jobs_router.get("/direct/{job_id}")
def get_direct_job(
    job_id: int,
    session: Session = Depends(get_session),
    current_user: TokenPayload | None = Depends(get_optional_user)
):
    return job_controller.get_job(session, job_id, listing_type=ListingType.Direct, current_user=current_user)

@jobs_router.post("/external")
def create_third_party_job(
    job_data: ThirdPartyJobCreate,
    session: Session = Depends(get_session),
    curr_user: TokenPayload = Depends(RoleChecker(["ADMIN"]))
):
    return job_controller.create_third_party_job(session, curr_user, job_data)

@jobs_router.put("/external/{job_id}")
def update_third_party_job(
    job_id: int,
    job_data: ThirdPartyJobUpdate,
    session: Session = Depends(get_session),
    curr_user: TokenPayload = Depends(RoleChecker(["ADMIN"]))
):
    return job_controller.update_third_party_job(session, curr_user, job_id, job_data)


# Category routes
@jobs_router.get("/categories")
def list_categories(session: Session = Depends(get_session)):
    return job_controller.list_categories(session)

@jobs_router.get("/categories/{category_id}")
def get_category(category_id: int, session: Session = Depends(get_session)):
    return job_controller.get_category(session, category_id)

@jobs_router.post("/categories")
def create_category(
    category_data: CategoryCreate,
    session: Session = Depends(get_session),
    curr_user: TokenPayload = Depends(RoleChecker(["ADMIN"]))
):
    return job_controller.create_category(session, category_data)

@jobs_router.put("/categories/{category_id}")
def update_category(
    category_id: int,
    category_data: CategoryUpdate,
    session: Session = Depends(get_session),
    curr_user: TokenPayload = Depends(RoleChecker(["ADMIN"]))
):
    return job_controller.update_category(session, category_id, category_data)

@jobs_router.delete("/categories/{category_id}")
def delete_category(
    category_id: int,
    session: Session = Depends(get_session),
    curr_user: TokenPayload = Depends(RoleChecker(["ADMIN"]))
):
    return job_controller.delete_category(session, category_id)
