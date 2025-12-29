from typing import Optional

from pydantic import BaseModel


class TutorialBase(BaseModel):
    name: str
    description: str


class TutorialUpdate(TutorialBase):
    name: Optional[str] = None
    description: Optional[str] = None
