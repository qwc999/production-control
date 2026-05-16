from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from src.data.models import Product
from src.data.repositories.base_repository import BaseRepository


class ProductRepository(BaseRepository[Product]):
    def __init__(self, session: AsyncSession):
        super().__init__(session, Product)

    async def get_by_batch_and_codes(self, batch_id: int, unique_codes: list[str]) -> list[Product]:
        query = (select(Product).
                 where(Product.batch_id == batch_id).
                 where(Product.unique_code.in_(unique_codes))
                 )
        result = await self.session.execute(query)
        return list(result.scalars().all())
