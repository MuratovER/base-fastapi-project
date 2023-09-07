from datetime import datetime

from sqlalchemy import Boolean, DateTime, Index
from sqlalchemy.orm import Mapped, mapped_column

from db.models.base import BaseModel
from db.models.mixins import IDMixin


class Quarter(BaseModel, IDMixin):
    """Quarter model."""

    is_active: Mapped[bool] = mapped_column(Boolean, nullable=False, default=False)
    started_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)
    finished_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)

    __table_args__ = (Index("only_one_active_quarter", is_active, unique=True, postgresql_where=is_active),)

    def __str__(self):
        return f"Quarter from {self.started_at} to {self.finished_at}"
