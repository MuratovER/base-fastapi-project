from sqlalchemy import Boolean, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from db.models.base import BaseModel
from db.models.mixins import CreatedAtMixin, IDMixin, UpdatedAtMixin


class Template(BaseModel, IDMixin, CreatedAtMixin, UpdatedAtMixin):
    """Template model."""

    name: Mapped[str] = mapped_column(String(length=255), nullable=False)
    is_archived: Mapped[bool] = mapped_column(Boolean, default=False)

    reviews: Mapped[list["Review"]] = relationship(  # type: ignore # noqa: F821
        "Review",
        back_populates="template",
        foreign_keys="Review.template_id",
    )
    questions: Mapped[list["Question"]] = relationship(  # type: ignore # noqa: F821
        "Question", back_populates="template", foreign_keys="Question.template_id"
    )

    def __str__(self):
        return f"Template #{self.id}"
