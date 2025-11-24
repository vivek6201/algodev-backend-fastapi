from app.modules.jobs.services.job_service import JobService
from app.modules.jobs.models.jobs import ListingType
from sqlmodel import Session
from app.modules.jobs.schemas.job_validations import ThirdPartyJobCreate, ThirdPartyJobUpdate
from app.modules.jobs.schemas.category_validations import CategoryCreate, CategoryUpdate
from app.common.lib.formatter import TokenPayload, SuccessResponse, ErrorResponse

class JobsController:
    def __init__(self):
        self.job_service = JobService()
    
    def create_third_party_job(self, session: Session, user: TokenPayload, job_data: ThirdPartyJobCreate):
        new_job = self.job_service.createThirdPartyJob(session, user, job_data)
        if not new_job:
            return ErrorResponse(message="Job with this slug already exists", status_code=400)
        return SuccessResponse(data=new_job, message="Job created successfully", status_code=201)

    def update_third_party_job(self, session: Session, user: TokenPayload, job_id: int, job_data: ThirdPartyJobUpdate):
        job = self.job_service.getJob(session, job_id)
        if not job:
            return ErrorResponse(message="Job not found", status_code=404)
        
        if job.owner_id != user.id and user.role != "ADMIN": # Assuming role check logic
             return ErrorResponse(message="Unauthorized to update this job", status_code=403)

        updated_job = self.job_service.updateThirdPartyJob(session, job_id, job_data)
        if not updated_job:
             return ErrorResponse(message="Failed to update job", status_code=400)
        
        return SuccessResponse(data=updated_job, message="Job updated successfully")

    def list_jobs(self, session: Session, listing_type: ListingType | None = None, current_user: TokenPayload | None = None):
        user_role = current_user.role if current_user else None
        jobs = self.job_service.listJobs(session, listing_type, user_role)
        return SuccessResponse(data=jobs, message="Jobs retrieved successfully")

    def get_job(self, session: Session, job_id: int, listing_type: ListingType | None = None, current_user: TokenPayload | None = None):
        user_role = current_user.role if current_user else None
        job = self.job_service.getJob(session, job_id, listing_type=listing_type, user_role=user_role)
        if not job:
            return ErrorResponse(message="Job not found", status_code=404)
        return SuccessResponse(data=job, message="Job retrieved successfully")

    # Category CRUD
    def list_categories(self, session: Session):
        categories = self.job_service.listCategories(session)
        return SuccessResponse(data=categories, message="Categories retrieved successfully")

    def get_category(self, session: Session, category_id: int):
        category = self.job_service.getCategory(session, category_id)
        if not category:
            return ErrorResponse(message="Category not found", status_code=404)
        return SuccessResponse(data=category, message="Category retrieved successfully")

    def create_category(self, session: Session, category_data: CategoryCreate):
        new_category = self.job_service.createCategory(session, category_data)
        if not new_category:
            return ErrorResponse(message="Category with this name already exists", status_code=400)
        return SuccessResponse(data=new_category, message="Category created successfully", status_code=201)

    def update_category(self, session: Session, category_id: int, category_data: CategoryUpdate):
        updated_category = self.job_service.updateCategory(session, category_id, category_data)
        if not updated_category:
            return ErrorResponse(message="Category not found", status_code=404)
        return SuccessResponse(data=updated_category, message="Category updated successfully")

    def delete_category(self, session: Session, category_id: int):
        success = self.job_service.deleteCategory(session, category_id)
        if not success:
            return ErrorResponse(message="Category not found", status_code=404)
        return SuccessResponse(message="Category deleted successfully")