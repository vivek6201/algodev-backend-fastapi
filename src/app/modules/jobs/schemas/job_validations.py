from datetime import datetime
from typing import List

from pydantic import BaseModel

from app.modules.jobs.models.jobs import JobBase, JobStatus, JobType, ListingType


class JobCreateBase(JobBase):
    category_id: List[int]
    min_salary: int
    max_salary: int
    slug: str | None = None


class JobUpdateBase(BaseModel):
    title: str | None = None
    description: str | None = None
    location: str | None = None
    min_salary: int | None = None
    max_salary: int | None = None
    slug: str | None = None
    job_type: JobType | None = None
    category_id: List[int] | None = None


class ThirdPartyJobCreate(JobCreateBase):
    external_apply_url: str
    listing_type: ListingType = ListingType.ThirdParty
    company_name: str


class ThirdPartyJobUpdate(JobUpdateBase):
    external_apply_url: str | None = None
    company_name: str | None = None


class DirectJobCreate(JobCreateBase):
    listing_type: ListingType = ListingType.Direct
    company_id: int


class DirectJobUpdate(JobUpdateBase):
    company_id: int | None = None


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
    min_salary: int | None = None
    max_salary: int | None = None
    listing_type: ListingType
    external_apply_url: str | None = None
    owner_id: int
    company_name: str | None = None
    company_id: int | None = None
    status: JobStatus
    categories: List[CategoryInJob] = []
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True
