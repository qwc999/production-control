from datetime import datetime, timezone, timedelta

from sqlalchemy.ext.asyncio import AsyncSession

from src.core.config import settings
from src.storage.minio_service import MinioService


class StorageCleanupService:
    def __init__(self):
        self.storage = MinioService()

    def cleanup_old_files(self, days: int = 30) -> dict:
        buckets = [
            settings.minio_exports_bucket,
            settings.minio_imports_bucket,
            settings.minio_reports_bucket
        ]
        deleted_by_bucket = {}
        total = 0

        threshold = datetime.now(timezone.utc) - timedelta(days=days)
        for bucket in buckets:
            deleted_by_bucket[bucket] = 0
            objects = self.storage.list_files(bucket)
            for obj in objects:
                if obj.last_modified is None:
                    continue
                if obj.last_modified < threshold:
                    self.storage.delete_file(
                        bucket_name=bucket,
                        object_name=obj.object_name
                    )
                    deleted_by_bucket[bucket] += 1
                    total += 1

        return {
            "success": True,
            "deleted": total,
            "buckets": deleted_by_bucket
        }
