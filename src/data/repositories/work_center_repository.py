from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from src.data.models.work_center import WorkCenter
from src.data.repositories.base_repository import BaseRepository


class WorkCenterRepository(BaseRepository[WorkCenter]):
    def __init__(self, session: AsyncSession):
        super().__init__(session, WorkCenter)

    async def get_one_or_create(self, identifier: str, name: str) -> WorkCenter:
        query = select(WorkCenter).where(WorkCenter.identifier == identifier)
        result = await self.session.execute(query)
        work_center = result.scalar_one_or_none()

        if work_center is None:
            work_center = WorkCenter(identifier=identifier, name=name)
            self.session.add(work_center)
            await self.session.flush()

        return work_center
