from datetime import datetime, timezone

from sqlalchemy.ext.asyncio import AsyncSession

from src.api.v1.schemas.batch import BatchCreate
from src.data.models.batch import Batch
from src.data.repositories.batch_repository import BatchRepository
from src.data.repositories.work_center_repository import WorkCenterRepository


class BatchService:
    def __init__(self, session: AsyncSession):
        self.session = session

        self.batch_repo = BatchRepository(session)
        self.work_center_repo = WorkCenterRepository(session)

    async def create_batches(self, items: list[BatchCreate]) -> list[Batch]:
        created = []
        for item in items:
            work_center = await self.work_center_repo.get_one_or_create(
                item.work_center_identifier,
                item.work_center_name
            )

            batch_data = {
                "is_closed": item.is_closed,
                "closed_at": datetime.now(timezone.utc) if item.is_closed else None,
                "task_description": item.task_description,
                "work_center_id": work_center.id,
                "shift": item.shift,
                "team": item.team,
                "batch_number": item.batch_number,
                "batch_date": item.batch_date,
                "nomenclature": item.nomenclature,
                "ekn_code": item.ekn_code,
                "shift_start": item.shift_start,
                "shift_end": item.shift_end
            }
            batch = await self.batch_repo.create(batch_data)
            created.append(batch)

        return created