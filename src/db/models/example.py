# from sqlalchemy import Boolean, Enum, ForeignKey, Integer, String
# from sqlalchemy.orm import Mapped, mapped_column, relationship
#
# from db.models import BaseModel
# from db.models.mixins import IDMixin
#
#
# class ExampleModel(BaseModel, IDMixin):
#     """User model."""
#
#     example_str: Mapped[str] = mapped_column(String(length=255), nullable=False)
#     example_enum: Mapped[ExampleEnum] = mapped_column(Enum(ExampleEnum), nullable=False)
#     example_bool: Mapped[bool] = mapped_column(Boolean, nullable=False, default=True)
#
#
#     def __str__(self):
#         return f"User #{self.username}"
