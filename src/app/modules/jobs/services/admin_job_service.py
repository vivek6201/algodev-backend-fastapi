from uuid import uuid4

from slugify import slugify
from sqlmodel import Session, select

from app.common.lib.formatter import TokenPayload
from app.modules.jobs.models.jobs import Category, Job
from app.modules.jobs.schemas.category_validations import CategoryCreate, CategoryUpdate
from app.modules.jobs.schemas.job_validations import ThirdPartyJobCreate, ThirdPartyJobUpdate
from app.modules.jobs.services.base_job_service import BaseJobService


class AdminJobService(BaseJobService):
    def create_category(self, session: Session, category_data: CategoryCreate):
        category = self.get_category(session=session, category_name=category_data.name)
        if category:
            return None

        category = Category(name=category_data.name)
        try:
            session.add(category)
            session.commit()
            session.refresh(category)
            return category
        except Exception as e:
            session.rollback()
            raise e

    def update_category(self, session: Session, category_id: int, category_data: CategoryUpdate):
        category = self.get_category(session=session, category_id=category_id)
        if not category:
            return None

        try:
            category.name = category_data.name
            session.add(category)
            session.commit()
            session.refresh(category)
            return category
        except Exception as e:
            session.rollback()
            raise e

    def create_job(
        self, session: Session, job_data: ThirdPartyJobCreate, current_admin: TokenPayload
    ):
        if not job_data.slug:
            base_slug = slugify(job_data.title)
            unique_suffix = str(uuid4().hex)[:6]
            job_data.slug = f"{base_slug}-{unique_suffix}"

        job = self.get_job(session=session, job_slug=job_data.slug, status=None)
        if job:
            return None

        # Bulk fetch categories
        categories = session.exec(
            select(Category).where(Category.id.in_(job_data.category_id))
        ).all()

        job_dict = job_data.model_dump(exclude={"category_id"})
        job = Job(**job_dict, admin_id=current_admin.id, categories=categories)

        try:
            session.add(job)
            session.commit()
            session.refresh(job)
            return job
        except Exception as e:
            session.rollback()
            raise e

    def update_job(
        self,
        session: Session,
        job_slug: str,
        job_data: ThirdPartyJobUpdate,
    ):
        job = self.get_job(session=session, job_slug=job_slug, status=None)
        if not job:
            return None

        try:
            job_dict = job_data.model_dump(exclude={"category_id"})

            for key, value in job_dict.items():
                setattr(job, key, value)

            if job_data.category_id is not None:
                # Fetch new categories
                new_categories = session.exec(
                    select(Category).where(Category.id.in_(job_data.category_id))
                ).all()
                # Unlink old categories and link new ones
                job.categories.clear()
                job.categories.extend(new_categories)

            session.add(job)
            session.commit()
            session.refresh(job)
            return job
        except Exception as e:
            session.rollback()
            raise e
