from sqlalchemy import Enum, ForeignKey, Integer
from sqlalchemy.orm import Mapped, mapped_column, relationship

from core.enums import ReviewStatusEnum
from db.models.base import BaseModel
from db.models.mixins import CreatedAtMixin, IDMixin, UpdatedAtMixin
from db.models.user import User


class Review(BaseModel, IDMixin, CreatedAtMixin, UpdatedAtMixin):
    """Review model."""

    evaluated_user_id: Mapped[int] = mapped_column(Integer, ForeignKey("users.id"), nullable=False)
    reviewer_id: Mapped[int] = mapped_column(Integer, ForeignKey("users.id"), nullable=False)
    template_id: Mapped[int] = mapped_column(Integer, ForeignKey("templates.id"), nullable=False)
    initiated_by_id: Mapped[int] = mapped_column(Integer, ForeignKey("users.id"), nullable=False)
    quarter_id: Mapped[int] = mapped_column(Integer, ForeignKey("quarters.id"), nullable=False)

    status: Mapped[ReviewStatusEnum] = mapped_column(
        Enum(ReviewStatusEnum), nullable=False, default=ReviewStatusEnum.PENDING
    )
    initiated_by: Mapped["User"] = relationship(  # noqa: F821
        "User",
        back_populates="reviews_initiated",
        foreign_keys="Review.initiated_by_id",
    )
    reviewer: Mapped["User"] = relationship(  # noqa: F821
        "User", back_populates="reviews_given", foreign_keys="Review.reviewer_id"
    )
    evaluated_user: Mapped["User"] = relationship(  # noqa: F821
        "User",
        back_populates="reviews_received",
        foreign_keys="Review.evaluated_user_id",
    )
    template: Mapped["Template"] = relationship(  # type: ignore # noqa: F821
        "Template", back_populates="reviews", foreign_keys="Review.template_id"
    )
    quarter: Mapped["Quarter"] = relationship("Quarter", foreign_keys="Review.quarter_id")  # type: ignore # noqa: F821
    answers: Mapped[list["Answer"]] = relationship(  # type: ignore # noqa: F821
        "Answer",
        back_populates="review",
        foreign_keys="Answer.review_id",
    )
    questions: Mapped[list["Question"]] = relationship(  # type: ignore # noqa: F821
        "Question",
        primaryjoin="Review.template_id==Question.template_id",
        foreign_keys="Question.template_id",
        viewonly=True,
    )

    def __str__(self):
        return f"Review #{self.id}"
