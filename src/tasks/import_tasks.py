import asyncio
from pathlib import Path
from tempfile import TemporaryDirectory

from src.cache.redis_cache import RedisCache
from src.core.config import settings
from src.domain.services.import_service import ImportService
from src.storage.minio_service import MinioService
from src.tasks.celery_app import celery_app
from src.tasks.database import celery_async_session_maker


@celery_app.task(bind=True, max_retries=1, name="reports.import_batches_from_file")
def import_batches_from_file_task(
    self,
    object_name: str
):
    return asyncio.run(_import_batches_from_file(
        task=self,
        object_name=object_name
    ))


async def _import_batches_from_file(task, object_name: str) -> dict:
    storage = MinioService()
    with TemporaryDirectory() as temp_dir:
        file_path = Path(temp_dir) / "batches_import.csv"

        storage.download_file(
            bucket_name=settings.minio_imports_bucket,
            object_name=object_name,
            file_path=str(file_path)
        )

        async with celery_async_session_maker() as session:
            service = ImportService(session)
            result = await service.import_batches_from_csv(
                file_path=file_path,
                callback=lambda current, total, created, skipped: task.update_state(
                    state="PROGRESS",
                    meta={
                        "current": current,
                        "total": total,
                        "created": created,
                        "skipped": skipped,
                        "progress": round(current / total * 100, 2) if total else 100,
                    },
                )
            )

            cache = RedisCache()
            try:
                await cache.delete_pattern("batches_list:*")
            finally:
                await cache.close()

            return result
