from sqlalchemy import ForeignKey, Integer, PrimaryKeyConstraint
from sqlalchemy.orm import Mapped, mapped_column

from db.models.base import BaseModel


class DepartmentTemplate(BaseModel):
    """DepartmentTemplate model is many to many for departments and templates."""

    department_id: Mapped[int] = mapped_column(Integer, ForeignKey("departments.id"))
    template_id: Mapped[int] = mapped_column(Integer, ForeignKey("templates.id"))

    __table_args__ = (PrimaryKeyConstraint("department_id", "template_id"),)

    def __str__(self):
        return f"DepartmentTemplate: department_id={self.department_id}; template_id={self.template_id}"
