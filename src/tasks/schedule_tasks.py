import asyncio

from src.domain.services.schedule_service import ScheduleService
from src.tasks.celery_app import celery_app
from src.tasks.database import celery_async_session_maker


@celery_app.task(bind=True,
                 name="schedule.auto_close_expired_batches")
def auto_close_expired_batches_task(self):
    return asyncio.run(_auto_close_expired_batches(
        task=self
    ))


async def _auto_close_expired_batches(task):
    async with celery_async_session_maker() as session:
        service = ScheduleService(session)
        return await service.auto_close_expired_batches()
