from typing import Sequence

from sqlalchemy import select

from db.models import DepartmentUser
from db.repositories.base import BaseDatabaseRepository


class DepartmentRepository(BaseDatabaseRepository):
    async def get_department_ids_by_user_id(self, user_id: int) -> Sequence[int]:
        query = select(DepartmentUser.department_id).filter_by(user_id=user_id)
        return (await self._session.scalars(query)).all()
