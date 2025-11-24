from pydantic import BaseModel
from typing import List
from app.modules.jobs.models.jobs import JobType, ListingType, JobBase


class JobCreateBase(JobBase):
    category_id: List[int]
    min_salary: int
    max_salary: int

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
