import asyncio

from src.api.v1.schemas.exports import BatchExportFilter
from src.domain.services.export_service import ExportService
from src.tasks.celery_app import celery_app
from src.tasks.database import celery_async_session_maker


@celery_app.task(bind=True, max_retries=3, name="reports.export_batches_to_csv")
def export_batches_to_csv_task(
    self,
    filters: dict
):
    return asyncio.run(_export_batches_to_csv(
        task=self,
        filters=filters
    ))


async def _export_batches_to_csv(task, filters: dict) -> dict:
    async with celery_async_session_maker() as session:
        service = ExportService(session)
        return await service.export_batches_to_csv(BatchExportFilter(**filters))
