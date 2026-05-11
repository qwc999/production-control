import asyncio

from src.domain.exceptions.exceptions import BatchNotFoundError
from src.domain.services.report_service import ReportService
from src.tasks.celery_app import celery_app
from src.tasks.database import celery_async_session_maker


@celery_app.task(bind=True,
                 max_retries=3,
                 name="reports.generate_batch_reports")
def generate_batch_reports_task(self,
    batch_id: int,
    report_format: str = "excel"
):
    return asyncio.run(_generate_batch_reports(
        task=self,
        batch_id=batch_id,
        report_format=report_format
    ))


async def _generate_batch_reports(task, batch_id: int, report_format: str) -> dict:
    async with celery_async_session_maker() as session:
        service = ReportService(session)

        try:
            if report_format == "excel":
                return await service.generate_batch_excel_report(batch_id)
        except BatchNotFoundError:
            return {
                "success": False,
                "error": "Batch not found",
            }
