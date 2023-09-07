from datetime import datetime
from typing import Sequence

from sqlalchemy import select

from db.models import Quarter
from db.repositories.base import BaseDatabaseRepository
from schemas.quarter import QuarterCreateSchema, QuarterUpdateSchema


class QuarterRepository(BaseDatabaseRepository):
    async def get_active_quarter(self) -> Quarter | None:
        query = select(Quarter).filter_by(is_active=True).order_by(Quarter.id.desc())

        query_result = await self._session.execute(query)

        return query_result.scalar_one_or_none()

    async def create_quarter(self, data_to_create: QuarterCreateSchema) -> Quarter:
        quarter = Quarter(**data_to_create.model_dump())
        self._session.add(quarter)
        await self._session.flush()

        return quarter

    async def get_quarters(self) -> Sequence[Quarter]:
        query = select(Quarter)
        query_result: Sequence[Quarter] = (await self._session.scalars(query)).all()
        return query_result

    async def update_quarter(self, quarter: Quarter, quarter_data: QuarterUpdateSchema):
        quarter.is_active = quarter_data.is_active
        quarter.started_at = quarter_data.started_at
        quarter.finished_at = quarter_data.finished_at
        await self._session.flush()

    async def get_quarter_by_id(self, quarter_id: int) -> Quarter | None:
        query = select(Quarter).where(Quarter.id == quarter_id)
        query_result = await self._session.execute(query)
        return query_result.scalar_one_or_none()

    async def get_quarter_by_date_gap(self, started_at: datetime, finished_at: datetime) -> Quarter | None:
        query = select(Quarter).where(Quarter.started_at <= started_at, Quarter.finished_at >= finished_at)
        query_result = await self._session.execute(query)
        return query_result.scalar_one_or_none()
