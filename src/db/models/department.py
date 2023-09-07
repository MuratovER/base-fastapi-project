from sqlalchemy import String
from sqlalchemy.orm import Mapped, mapped_column

from db.models import BaseModel
from db.models.mixins import IDMixin


class Department(BaseModel, IDMixin):
    """User department."""

    name: Mapped[str] = mapped_column(String(length=255), unique=True, nullable=False)

    def __str__(self):
        return f"Department #{self.name}"
