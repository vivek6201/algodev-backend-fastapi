from app.modules.jobs.schemas.job_validations import ThirdPartyJobCreate, DirectJobCreate
from sqlmodel import Session, select
from app.modules.jobs.models.jobs import Job, JobStatus, Category
from typing import Optional
from app.common.lib.formatter import TokenPayload


class JobService:
    def getJob(self, session: Session, job_id: Optional[int], slug: Optional[str] = None):
        job = None

        if slug:
            job = session.exec(select(Job).where(Job.slug == slug)).first()

        if job_id:
            job = session.get(Job, job_id)

        return job
    
    def getCategories(self, session: Session, category_ids: list[int]):
        categories = session.exec(select(Category).where(Category.id.in_(category_ids))).all()
        return categories

    def createThirdPartyJob(self, session: Session, user: TokenPayload, job_data: ThirdPartyJobCreate):
        job = self.getJob(session, None, job_data.slug)

        if job:
            return None

        job_dict = job_data.model_dump(exclude={"category_id"})
        new_job = Job(
            **job_dict,
            owner_id=user.id
        )

        if job_data.category_id:
            categories = self.getCategories(session, job_data.category_id)
            new_job.categories = categories
        session.add(new_job)
        session.commit()
        session.refresh(new_job)

        return new_job

    def createDirectJob(self, session: Session, job_data: DirectJobCreate):
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
        jobs = session.exec(select(Job).where(
            Job.status == JobStatus.PUBLISHED)).all()
        return jobs

    def listAllJobs(self, session: Session):
        jobs = session.exec(select(Job)).all()
        return jobs
