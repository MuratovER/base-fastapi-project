"""
Directory for describing repositories for work with database.

Repository example:
from sqlalchemy import select

from db.repositories.base import BaseDatabaseRepository


class SomeModelDatabaseRepository(BaseDatabaseRepository):
    async def get_by_id(id: int) -> SomeModel:
        stmt = select(SomeModel).filter(SomeModel.id == id)
        instance = (await self._session.scalars(stmt)).first()

        if instance is None:
            raise NotFoundException

        return instance

"""
