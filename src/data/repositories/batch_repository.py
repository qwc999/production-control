from sqlalchemy.ext.asyncio import AsyncSession

from src.data.models.batch import Batch
from src.data.repositories.base_repository import BaseRepository


class BatchRepository(BaseRepository[Batch]):
    def __init__(self, session: AsyncSession):
        super().__init__(session, Batch)