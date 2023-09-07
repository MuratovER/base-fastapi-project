from sqlalchemy import ForeignKey, Integer, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from db.models.base import BaseModel
from db.models.mixins import IDMixin


class Answer(BaseModel, IDMixin):
    """Answer model."""

    reviewer_id: Mapped[int] = mapped_column(Integer, ForeignKey("users.id"), nullable=False)
    question_id: Mapped[int] = mapped_column(Integer, ForeignKey("questions.id"), nullable=False)
    review_id: Mapped[int] = mapped_column(Integer, ForeignKey("reviews.id"), nullable=False)
    text: Mapped[str] = mapped_column(Text, nullable=False)

    question: Mapped["Question"] = relationship(  # type: ignore # noqa: F821
        "Question", back_populates="answers", foreign_keys="Answer.question_id"
    )
    reviewer: Mapped["User"] = relationship(  # type: ignore # noqa: F821
        "User", back_populates="answers", foreign_keys="Answer.reviewer_id"
    )

    review: Mapped["Review"] = relationship(  # type: ignore # noqa: F821
        "Review", back_populates="answers", foreign_keys="Answer.review_id"
    )

    def __str__(self):
        return f"Answer #{self.id}"
