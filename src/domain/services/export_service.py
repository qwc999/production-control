from datetime import datetime, timezone, timedelta
from pathlib import Path
from tempfile import TemporaryDirectory

from sqlalchemy.ext.asyncio import AsyncSession

from src.api.v1.schemas.exports import BatchExportFilter
from src.core.config import settings
from src.data.repositories.batch_repository import BatchRepository
from src.reports.batch_report_csv_export import generate_batches_csv_export
from src.storage.minio_service import MinioService


class ExportService:
    def __init__(self, session: AsyncSession):
        self.session = session
        self.batch_repo = BatchRepository(session)
        self.storage = MinioService()

    async def export_batches_to_csv(
            self,
            filters: BatchExportFilter
    ):
        batches = await self.batch_repo.get_by_filter_for_export(filters)

        timestamp = datetime.now(timezone.utc).strftime("%Y%m%d_%H%M%S")
        file_name = f"batches_export_{timestamp}.csv"
        object_name = f"batch_exports/{file_name}"
        expires_at = datetime.now(timezone.utc) + timedelta(days=7)

        with TemporaryDirectory() as temp_dir:
            file_path = Path(temp_dir) / file_name
            generate_batches_csv_export(batches, file_path)

            file_size = file_path.stat().st_size
            file_url = self.storage.upload_file(
                bucket_name=settings.minio_exports_bucket,
                file_path=str(file_path),
                object_name=object_name
            )

        return {
            "success": True,
            "file_url": file_url,
            "file_name": file_name,
            "file_size": file_size,
            "expires_at": expires_at.isoformat(),
            "total_batches": len(batches),
        }
    