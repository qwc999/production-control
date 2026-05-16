from datetime import datetime

from sqlalchemy import select, Select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from src.api.v1.schemas.batch import BatchFilter
from src.api.v1.schemas.exports import BatchExportFilter
from src.data.models import WorkCenter
from src.data.models.batch import Batch
from src.data.repositories.base_repository import BaseRepository


class BatchRepository(BaseRepository[Batch]):
    def __init__(self, session: AsyncSession):
        super().__init__(session, Batch)

    async def get_by_id_with_products(self, batch_id: int) -> Batch | None:
        query = (
            select(Batch).
            options(selectinload(Batch.products)).
            where(Batch.id == batch_id)
        )
        result = await self.session.execute(query)
        return result.scalar_one_or_none()

    async def get_by_filter(self, filters: BatchFilter) -> list[Batch]:
        query = select(Batch)
        query = await self._apply_filters(query, filters)

        query = (query.
                 order_by(Batch.id).
                 offset(filters.offset).
                 limit(filters.limit))
        result = await self.session.execute(query)
        return list(result.scalars().all())

    async def get_by_filter_for_export(self, filters: BatchExportFilter) -> list[Batch]:
        query = select(Batch)
        query = await self._apply_filters(query, filters)

        query = (query.order_by(Batch.id))
        result = await self.session.execute(query)
        return list(result.scalars().all())

    async def close_expired_batches(self, now: datetime) -> int:
        query = (select(Batch).
                 where(Batch.is_closed.is_(False)).
                 where(Batch.shift_end <= now))

        result = await self.session.execute(query)
        batches = list(result.scalars().all())
        for batch in batches:
            batch.is_closed = True
            batch.closed_at = now

        await self.session.commit()
        return len(batches)

    async def _apply_filters(
            self,
            query: Select,
            filters: BatchFilter | BatchExportFilter
    ) -> Select:
        if filters.is_closed is not None:
            query = query.where(Batch.is_closed == filters.is_closed)

        if filters.batch_number is not None:
            query = query.where(Batch.batch_number == filters.batch_number)

        if filters.batch_date is not None:
            query = query.where(Batch.batch_date == filters.batch_date)

        if filters.work_center_identifier is not None:
            query = (
                query
                .join(Batch.work_center)
                .where(WorkCenter.identifier == filters.work_center_identifier)
            )

        if filters.shift is not None:
            query = query.where(Batch.shift == filters.shift)
        return query
