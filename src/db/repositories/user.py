# import typing
# from typing import Sequence
#
# from sqlalchemy import and_, select
#
# from db.models import Review, User
# from db.repositories.base import BaseDatabaseRepository
#
#
# class ExampleRepository(BaseDatabaseRepository):
#     """Class contains methods to fetch data from db."""
#
#     async def example_get_object(self, object_param):
#         query = select(ExampleClass).filter_by(object_param=object_param)
#         query_result = await self._session.execute(query)
#         return query_result.scalar_one_or_none()
#
#     async def example_get_all_objects(self, object_param) -> Sequence[ExampleClass]:
#         query = select(ExampleClass).filter_by(object_param=object_param)
#         return (await self._session.scalars(query)).all()
#
#     async def example_update_object(self,new_object_param, example_class) -> None:
#         example_class.object_param = new_object_param
#
#         await self._session.flush()
