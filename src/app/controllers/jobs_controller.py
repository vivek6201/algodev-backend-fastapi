from app.services.job_service import JobService
from sqlmodel import Session
class JobsController:
    def __init__(self):
        self.job_service = JobService()
    
    # async def create_job(self, data: dict, session: Session):
    #     new_job = self.job_service.create_job(data, session)
    #     return new_job