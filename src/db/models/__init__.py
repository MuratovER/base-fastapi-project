"""
Directory for describing models.

Import model here to enable alembic autogenerate.

Model example:
from sqlalchemy import BigInteger, String
from sqlalchemy.orm import Mapped, mapped_column


class SomeModel(BaseModel):
    id: Mapped[int] = mapped_column(BigInteger, primary_key=True, autoincrement=True)
    some_field: Mapped[str] = mapped_column(String(length=255), nullable=False)

    def __str__(self) -> str:
        return f"Some model #{self.id}"
"""

__all__ = (
    "BaseModel",
    "Review",
    "Quarter",
    "Template",
    "DepartmentTemplate",
    "Question",
    "Answer",
    "DepartmentUser",
    "User",
    "Department",
)


from db.models.answer import Answer
from db.models.base import BaseModel
from db.models.department import Department
from db.models.department_template import DepartmentTemplate
from db.models.department_user import DepartmentUser
from db.models.quarter import Quarter
from db.models.question import Question
from db.models.review import Review
from db.models.template import Template
from db.models.user import User
