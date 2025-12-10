from datetime import datetime
from enum import Enum
from typing import List, Optional

from sqlmodel import Column, Field, ForeignKey, Relationship, SQLModel

from app.common.db.utils import pg_enum


class JobType(Enum):
    FULL_TIME = "FULL_TIME"
    PART_TIME = "PART_TIME"
    CONTRACT = "CONTRACT"
    INTERN = "INTERN"


class JobMode(Enum):
    REMOTE = "REMOTE"
    ON_SITE = "ON_SITE"
    HYBRID = "HYBRID"


class JobStatus(Enum):
    DRAFT = "DRAFT"
    PUBLISHED = "PUBLISHED"


class ListingType(Enum):
    ThirdParty = "ThirdParty"
    Direct = "Direct"


class ApplicationStatus(Enum):
    APPLIED = "APPLIED"
    SHORTLISTED = "SHORTLISTED"
    REJECTED = "REJECTED"
    HIRED = "HIRED"


class JobCategoryLink(SQLModel, table=True):
    # Composite Primary Key (Both keys together are unique)
    job_id: Optional[int] = Field(default=None, foreign_key="job.id", primary_key=True)
    category_id: Optional[int] = Field(
        default=None,
        sa_column=Column(ForeignKey("category.id", ondelete="CASCADE"), primary_key=True),
    )


class Category(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True, index=True)
    name: str = Field(index=True, unique=True)
    jobs: List["Job"] = Relationship(back_populates="categories", link_model=JobCategoryLink)


class Company(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True, index=True)
    name: str
    logo_url: Optional[str] = None
    website: Optional[str] = None

    # A company has many jobs
    jobs: List["Job"] = Relationship(back_populates="company_rel")

    created_at: datetime = Field(default_factory=datetime.now)


class JobBase(SQLModel):
    title: str
    slug: str = Field(index=True, unique=True)
    description: str
    location: str
    job_type: JobType = pg_enum(JobType, nullable=False)
    job_mode: JobMode = pg_enum(JobMode, nullable=False)
    min_salary: Optional[int] = None
    max_salary: Optional[int] = None
    listing_type: ListingType = pg_enum(ListingType, nullable=False)


class Job(JobBase, table=True):
    id: Optional[int] = Field(default=None, primary_key=True, index=True)

    # Fields specific to Job table (not in Base because they might be conditional or system managed)
    external_apply_url: Optional[str] = None

    categories: List["Category"] = Relationship(back_populates="jobs", link_model=JobCategoryLink)

    owner_id: Optional[int] = Field(default=None, foreign_key="users.id")
    owner: Optional["Users"] = Relationship(back_populates="posted_jobs")  # noqa: F821

    admin_id: Optional[int] = Field(default=None, foreign_key="admin.id")
    admin: Optional["Admin"] = Relationship(back_populates="posted_jobs")  # noqa: F821

    company_name: Optional[str] = None

    company_id: Optional[int] = Field(default=None, foreign_key="company.id")
    company_rel: Optional[Company] = Relationship(back_populates="jobs")
    status: JobStatus = pg_enum(JobStatus, default=JobStatus.DRAFT)

    applications: List["JobApplication"] = Relationship(back_populates="job")

    created_at: datetime = Field(default_factory=datetime.now)
    updated_at: datetime = Field(
        default_factory=datetime.now, sa_column_kwargs={"onupdate": datetime.now}
    )


class JobApplication(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True, index=True)

    # Links
    job_id: int = Field(foreign_key="job.id")
    job: Optional[Job] = Relationship(back_populates="applications")

    candidate_id: int = Field(foreign_key="users.id")
    candidate: Optional["Users"] = Relationship(back_populates="applications")  # noqa: F821

    # Application Data
    resume_url: str
    cover_letter: Optional[str] = None

    # Recruiter Actions
    status: ApplicationStatus = pg_enum(ApplicationStatus, default=ApplicationStatus.APPLIED)
    recruiter_notes: Optional[str] = None

    applied_at: datetime = Field(default_factory=datetime.now)
