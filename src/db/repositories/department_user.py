import typing

from sqlalchemy import select

from db.models import DepartmentUser, User
from db.repositories.base import BaseDatabaseRepository


class DepartmentUserRepository(BaseDatabaseRepository):
    async def get_department_ids_for_user(self, user: User) -> typing.Sequence[int]:
        query = select(DepartmentUser.department_id).filter(DepartmentUser.user_id == user.id)
        query_result = await self._session.execute(query)
        department_ids = query_result.scalars().all()

        return department_ids

    async def get_users_by_department_ids(self, department_ids: typing.Iterable[int]) -> typing.Sequence[User]:
        sub_query = select(DepartmentUser.user_id).where(DepartmentUser.department_id.in_(department_ids))
        query = select(User).where(User.id.in_(sub_query))
        return (await self._session.scalars(query)).all()

    async def get_user_ids_by_department_ids(self, department_ids: typing.Iterable[int]) -> typing.Sequence[int]:
        query = select(DepartmentUser.user_id).where(DepartmentUser.department_id.in_(department_ids))
        return (await self._session.scalars(query)).all()
