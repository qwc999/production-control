from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from src.api.v1.schemas.batch import BatchFilter
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

        query = (query.
                 order_by(Batch.id).
                 offset(filters.offset).
                 limit(filters.limit))
        result = await self.session.execute(query)
        return list(result.scalars().all())
