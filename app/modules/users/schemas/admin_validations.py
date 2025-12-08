from typing import Optional

from pydantic import BaseModel


class AdminCreate(BaseModel):
    first_name: str
    last_name: str
    email: str
    password: str


class AdminUpdate(BaseModel):
    first_name: Optional[str] = None
    last_name: Optional[str] = None
    password: Optional[str] = None
