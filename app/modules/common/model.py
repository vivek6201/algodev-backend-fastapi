from datetime import datetime
from typing import Optional

from sqlmodel import Field, SQLModel


class SoftDeleteMixin(SQLModel):
    deleted_at: Optional[datetime] = Field(
        default=None,
        index=True,
    )

    def soft_delete(self):
        self.deleted_at = datetime.utcnow()

    def restore(self):
        self.deleted_at = None
