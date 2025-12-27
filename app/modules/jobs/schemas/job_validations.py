from datetime import datetime
from typing import List, Optional

from pydantic import BaseModel

from app.modules.jobs.models.jobs import JobBase, JobMode, JobStatus, JobType, ListingType


class JobCreateBase(JobBase):
    category_id: List[int]
    min_salary: int
    max_salary: int
    slug: str | None = None


class JobUpdateBase(BaseModel):
    title: Optional[str] = None
    description: Optional[str] = None
    location: Optional[str] = None
    min_salary: Optional[int] = None
    max_salary: Optional[int] = None
    slug: Optional[str] = None
    job_type: Optional[JobType] = None
    job_mode: Optional[JobMode] = None
    category_id: Optional[List[int]] = None
    status: Optional[JobStatus] = None
    min_experience: Optional[int] = None
    max_experience: Optional[int] = None


class JobStatusUpdate(BaseModel):
    status: JobStatus


class ThirdPartyJobCreate(JobCreateBase):
    external_apply_url: str
    listing_type: ListingType = ListingType.ThirdParty
    company_name: str


class ThirdPartyJobUpdate(JobUpdateBase):
    external_apply_url: Optional[str] = None
    company_name: Optional[str] = None


class DirectJobCreate(JobCreateBase):
    listing_type: ListingType = ListingType.Direct
    company_id: int


class DirectJobUpdate(JobUpdateBase):
    company_id: Optional[int] = None


# Response schemas
class CategoryInJob(BaseModel):
    """Nested category representation in job response"""

    id: int
    name: str

    class Config:
        from_attributes = True


class JobResponse(BaseModel):
    """Job response schema with all fields including categories"""

    id: int
    title: str
    slug: str
    description: str
    location: str
    job_type: JobType
    job_mode: JobMode
    min_salary: Optional[int] = None
    max_salary: Optional[int] = None
    min_experience: int
    max_experience: int
    listing_type: ListingType
    external_apply_url: Optional[str] = None
    admin_id: Optional[int] = None
    owner_id: Optional[int] = None
    company_name: Optional[str] = None
    company_id: Optional[int] = None
    status: Optional[JobStatus] = None
    categories: List[CategoryInJob] = []
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


class CompactJobResponse(BaseModel):
    """Short job response schema"""

    id: int
    title: str
    slug: str
    location: str
    job_type: JobType
    job_mode: JobMode
    min_salary: int
    max_salary: int
    min_experience: int
    max_experience: int
    listing_type: ListingType
    company_name: str
    status: JobStatus
    company_id: Optional[int] = None
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True
