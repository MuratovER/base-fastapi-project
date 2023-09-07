from sqlalchemy import Boolean, Enum, ForeignKey, Integer, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from core.enums import UserRoleEnum
from db.models import BaseModel


class User(BaseModel):
    """User model."""

    __allow_unmapped__ = True

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True, autoincrement=True)
    mentored_by_id: Mapped[int | None] = mapped_column(Integer, ForeignKey("users.id"), nullable=True)
    username: Mapped[str] = mapped_column(String(length=255), nullable=False)
    email: Mapped[str] = mapped_column(String(length=255), unique=True, nullable=False)
    password: Mapped[str] = mapped_column(String(length=255), nullable=False)
    first_name: Mapped[str | None] = mapped_column(String(length=255), nullable=True)
    last_name: Mapped[str | None] = mapped_column(String(length=255), nullable=True)
    father_name: Mapped[str | None] = mapped_column(String(length=255), nullable=True)
    role: Mapped[UserRoleEnum] = mapped_column(Enum(UserRoleEnum), nullable=False)
    auth_token: Mapped[str | None] = mapped_column(String(length=513), unique=True, nullable=True)
    is_active: Mapped[bool] = mapped_column(Boolean, nullable=False, default=True)

    avatar_key: Mapped[str | None] = mapped_column(String, default=None, nullable=True)
    avatar: str | None = None

    mentored_by: Mapped["User"] = relationship("User", back_populates="mentees", remote_side="User.id")
    mentees: Mapped[list["User"]] = relationship("User", back_populates="mentored_by")

    answers: Mapped[list["Answer"]] = relationship(  # type: ignore # noqa: F821
        "Answer",
        back_populates="reviewer",
        foreign_keys="Answer.reviewer_id",
    )

    reviews_given: Mapped[list["Review"]] = relationship(  # type: ignore # noqa: F821
        "Review",
        back_populates="reviewer",
        foreign_keys="Review.reviewer_id",
    )
    reviews_received: Mapped[list["Review"]] = relationship(  # type: ignore # noqa: F821
        "Review",
        back_populates="evaluated_user",
        foreign_keys="Review.evaluated_user_id",
    )
    reviews_initiated: Mapped[list["Review"]] = relationship(  # type: ignore # noqa: F821
        "Review",
        back_populates="initiated_by",
        foreign_keys="Review.initiated_by_id",
    )

    def __str__(self):
        return f"User #{self.username}"
