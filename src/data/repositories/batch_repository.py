from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

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
