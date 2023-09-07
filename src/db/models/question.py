from sqlalchemy import ForeignKey, Integer, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from db.models.base import BaseModel
from db.models.mixins import IDMixin


class Question(BaseModel, IDMixin):
    """Question model."""

    template_id: Mapped[int] = mapped_column(Integer, ForeignKey("templates.id"), nullable=False)
    text: Mapped[str] = mapped_column(Text, nullable=False)
    description: Mapped[str | None] = mapped_column(Text, nullable=True)

    answers: Mapped[list["Answer"]] = relationship(  # type: ignore # noqa: F821
        "Answer", back_populates="question", viewonly=True
    )
    template: Mapped["Template"] = relationship("Template", back_populates="questions")  # type: ignore # noqa: F821

    def __str__(self):
        return f"Question #{self.id}"
