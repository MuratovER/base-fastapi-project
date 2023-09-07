import typing
from uuid import uuid4

from fastapi import Depends
from pydantic import ValidationError
from sqlalchemy.ext.asyncio import AsyncSession

from db.redis import AsyncRedis, get_redis
from db.session import get_session
from schemas.base import BaseKeySchema, BaseOrmSchema


class BaseDatabaseRepository:
    _session: AsyncSession

    def __init__(self, session: AsyncSession = Depends(get_session)) -> None:
        self._session = session


class BaseRedisRepository:
    schema: typing.Type[BaseOrmSchema]
    key_schema: BaseKeySchema

    def __init__(self, session: AsyncRedis = Depends(get_redis)) -> None:
        self._session = session

    def get_key(self, uuid: str):
        return self.key_schema.get_key(uuid)

    async def get(self, uuid: str) -> BaseOrmSchema | None:
        value = await self._session.get(self.get_key(uuid=uuid))

        try:
            return self.schema.model_validate_json(str(value))
        except ValidationError:
            return None

    async def set(self, model: BaseOrmSchema, expiration_seconds: int | None = None) -> str:
        if not isinstance(model, self.schema):
            raise ValueError("Model scheme is not similar with repository scheme")

        uuid = str(uuid4())
        key = self.get_key(uuid=uuid)
        value = model.model_dump_json()

        if expiration_seconds:
            await self._session.setex(name=key, time=expiration_seconds, value=value)
        else:
            await self._session.set(name=key, value=value)

        return uuid

    async def delete(self, uuid: str) -> None:
        await self._session.delete(self.get_key(uuid=uuid))
