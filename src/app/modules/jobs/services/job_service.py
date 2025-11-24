from typing import Optional

from sqlalchemy.orm import selectinload
from sqlmodel import Session, select

from app.common.lib.formatter import TokenPayload
from app.modules.jobs.models.jobs import Category, Job, JobStatus, ListingType
from app.modules.jobs.schemas.category_validations import CategoryCreate, CategoryUpdate
from app.modules.jobs.schemas.job_validations import ThirdPartyJobCreate, ThirdPartyJobUpdate


class JobService:
    def getJob(
        self,
        session: Session,
        job_id: Optional[int],
        slug: Optional[str] = None,
        listing_type: Optional[ListingType] = None,
        user_role: Optional[str] = None,
    ):
        job = None

        if slug:
            # Eager load categories
            query = select(Job).options(selectinload(Job.categories)).where(Job.slug == slug)
            if listing_type:
                query = query.where(Job.listing_type == listing_type)
            # Filter by status based on user role
            if user_role not in ["ADMIN", "MODERATOR", "RECRUITER"]:
                query = query.where(Job.status == JobStatus.PUBLISHED)
            job = session.exec(query).first()

        if job_id:
            # Eager load categories for job_id query
            query = select(Job).options(selectinload(Job.categories)).where(Job.id == job_id)
            job = session.exec(query).first()

            # If listing_type is specified, verify the job matches
            if job and listing_type and job.listing_type != listing_type:
                return None
            # Filter by status based on user role
            if (
                job
                and user_role not in ["ADMIN", "MODERATOR", "RECRUITER"]
                and job.status != JobStatus.PUBLISHED
            ):
                return None

        return job

    def getCategories(self, session: Session, category_ids: list[int]):
        categories = session.exec(select(Category).where(Category.id.in_(category_ids))).all()
        return categories

    def createThirdPartyJob(
        self, session: Session, user: TokenPayload, job_data: ThirdPartyJobCreate
    ):
        job = self.getJob(session, None, job_data.slug)

        if job:
            return None

        job_dict = job_data.model_dump(exclude={"category_id"})
        new_job = Job(**job_dict, owner_id=user.id)

        if job_data.category_id:
            categories = self.getCategories(session, job_data.category_id)
            new_job.categories = categories
        session.add(new_job)
        session.commit()
        session.refresh(new_job)

        return new_job
        job = self.getJob(session, None, job_data.slug)

        if job:
            return None

        job_dict = job_data.model_dump(exclude={"category_id"})
        new_job = Job(**job_dict)

        if job_data.category_id:
            categories = self.getCategories(session, job_data.category_id)
            new_job.categories = categories
        session.add(new_job)
        session.commit()
        session.refresh(new_job)
        return new_job

    def listPublicJobs(self, session: Session):
        jobs = session.exec(select(Job).where(Job.status == JobStatus.PUBLISHED)).all()
        return jobs

    def listJobs(
        self,
        session: Session,
        listing_type: Optional[ListingType] = None,
        user_role: Optional[str] = None,
    ):
        """List jobs with optional listing_type filter and role-based access control"""
        # Eager load categories so they're included in the response
        query = select(Job).options(selectinload(Job.categories))

        if listing_type:
            query = query.where(Job.listing_type == listing_type)
        # Filter by status based on user role
        if user_role not in ["ADMIN", "MODERATOR", "RECRUITER"]:
            query = query.where(Job.status == JobStatus.PUBLISHED)
        jobs = session.exec(query).all()
        return jobs

    def updateThirdPartyJob(self, session: Session, job_id: int, job_data: ThirdPartyJobUpdate):
        job = self.getJob(session, job_id)
        if not job:
            return None

        if job.listing_type != ListingType.ThirdParty:
            return None

        job_dict = job_data.model_dump(exclude_unset=True, exclude={"category_id"})
        for key, value in job_dict.items():
            setattr(job, key, value)

        if job_data.category_id is not None:
            categories = self.getCategories(session, job_data.category_id)
            job.categories = categories

        session.add(job)
        session.commit()
        session.refresh(job)
        return job

    # Category CRUD operations
    def listCategories(self, session: Session):
        categories = session.exec(select(Category)).all()
        return categories

    def getCategory(self, session: Session, category_id: int):
        category = session.get(Category, category_id)
        return category

    def createCategory(self, session: Session, category_data: CategoryCreate):
        # Check if category with same name exists
        existing = session.exec(select(Category).where(Category.name == category_data.name)).first()
        if existing:
            return None

        new_category = Category(**category_data.model_dump())
        session.add(new_category)
        session.commit()
        session.refresh(new_category)
        return new_category

    def updateCategory(self, session: Session, category_id: int, category_data: CategoryUpdate):
        category = self.getCategory(session, category_id)
        if not category:
            return None

        category_dict = category_data.model_dump(exclude_unset=True)
        for key, value in category_dict.items():
            setattr(category, key, value)

        session.add(category)
        session.commit()
        session.refresh(category)
        return category

    def deleteCategory(self, session: Session, category_id: int):
        category = self.getCategory(session, category_id)
        if not category:
            return False

        session.delete(category)
        session.commit()
        return True
