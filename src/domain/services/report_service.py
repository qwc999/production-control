from datetime import datetime, timezone, timedelta
from pathlib import Path
from tempfile import TemporaryDirectory

from sqlalchemy.ext.asyncio import AsyncSession

from src.core.config import settings
from src.data.repositories.batch_repository import BatchRepository
from src.domain.exceptions.exceptions import BatchNotFoundError
from src.reports.batch_report_excel import generate_batch_report_excel
from src.storage.minio_service import MinioService


class ReportService:
    def __init__(self, session: AsyncSession):
        self.session = session
        self.batch_repo = BatchRepository(session)
        self.storage = MinioService()

    async def generate_batch_excel_report(self, batch_id: int) -> dict:
        batch = await self.batch_repo.get_by_id_with_products(batch_id)
        if batch is None:
            raise BatchNotFoundError

        file_name = f"batch_{batch_id}.xlsx"
        object_name = f"batch_reports/{file_name}"
        expires_at = datetime.now(timezone.utc) + timedelta(days=7)

        with TemporaryDirectory() as temp_dir:
            file_path = Path(temp_dir) / file_name
            generate_batch_report_excel(batch, str(file_path))

            file_url = self.storage.upload_file(
                bucket_name=settings.minio_reports_bucket,
                file_path=str(file_path),
                object_name=object_name
            )
            file_size = file_path.stat().st_size

        return {
            "success": True,
            "file_url": file_url,
            "file_name": file_name,
            "file_size": file_size,
            "expires_at": expires_at.isoformat()
        }
