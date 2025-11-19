from sqlmodel import Relationship, SQLModel, Field
from typing import List, Optional
from datetime import datetime
from enum import Enum

class JobType(Enum):
    FULL_TIME = "FULL_TIME"
    PART_TIME = "PART_TIME"
    CONTRACT = "CONTRACT"
    INTERN = "INTERN"


class PostStatus(Enum):
    DRAFT = "DRAFT"
    PUBLISHED = "PUBLISHED"


class Company(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True, index=True)
    name: str
    jobs: List["Jobs"] = Relationship(back_populates="company", cascade_delete=True)

    created_at: datetime = Field(default_factory=datetime.now)


class Jobs(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True, index=True)
    title: str
    short_description: str
    long_description: Optional[str] = None

    company_id: int = Field(foreign_key="company.id")
    company: Optional[Company] = Relationship(back_populates="jobs")
    location: str
    job_type: JobType

    min_exp: Optional[int] = None
    max_exp: Optional[int] = None
    min_salary: Optional[float] = None
    max_salary: Optional[float] = None
    post_status: PostStatus = Field(default=PostStatus.DRAFT)

    created_at: datetime = Field(default_factory=datetime.now)
    updated_at: datetime = Field(default_factory=datetime.now, sa_column_kwargs={
                                 "onupdate": datetime.now})