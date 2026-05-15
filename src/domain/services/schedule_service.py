from datetime import datetime, timezone

from sqlalchemy.ext.asyncio import AsyncSession

from src.data.repositories.batch_repository import BatchRepository


class ScheduleService:
    def __init__(self, session: AsyncSession):
        self.session = session
        self.batch_repo = BatchRepository(session)

    async def auto_close_expired_batches(self) -> dict:
        now = datetime.now(timezone.utc)
        closed_batches = await self.batch_repo.close_expired_batches(now)

        return {
            "success": True,
            "closed_batches": closed_batches
        }