from sqlalchemy import ForeignKey, Integer, PrimaryKeyConstraint
from sqlalchemy.orm import Mapped, mapped_column

from db.models import BaseModel


class DepartmentUser(BaseModel):
    """Intermediate table for ManyToMany relationship between User and Department."""

    user_id: Mapped[int] = mapped_column(Integer, ForeignKey("users.id"))
    department_id: Mapped[int] = mapped_column(Integer, ForeignKey("departments.id"))

    __table_args__ = (PrimaryKeyConstraint("user_id", "department_id"),)

    def __str__(self):
        return f"DepartmentUser user={self.user_id} department={self.department_id}"
