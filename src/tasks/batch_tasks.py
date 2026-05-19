import asyncio

from src.cache.cache_keys import batch_detail_key, dashboard_key, batch_statistics_key
from src.cache.redis_cache import RedisCache
from src.tasks.database import celery_async_session_maker

from src.domain.exceptions.exceptions import BatchNotFoundError, BatchClosedError
from src.domain.services.batch_service import BatchService
from src.tasks.celery_app import celery_app


@celery_app.task(bind=True,
                 max_retries=3,
                 name="batches.aggregate_products")
def aggregate_products_task(self,
    batch_id: int,
    unique_codes: list[str]
):
    return asyncio.run(_aggregate_products(
        task=self,
        batch_id=batch_id,
        unique_codes=unique_codes
    ))


async def _aggregate_products(task, batch_id: int, unique_codes: list[str]) -> dict:
    async with celery_async_session_maker() as session:
        service = BatchService(session)

        try:
            result = await service.aggregate_products(
                batch_id=batch_id,
                unique_codes=unique_codes,
                progress_callback=lambda current, total: task.update_state(
                    state="PROGRESS",
                    meta={
                        "current": current,
                        "total": total,
                        "progress": round(current / total * 100, 2)
                    }
                )
            )
        except BatchNotFoundError:
            return {
                "success": False,
                "total": len(unique_codes),
                "aggregated": 0,
                "failed": len(unique_codes),
                "errors": [
                    {
                        "code": code,
                        "message": "Batch not found",
                    }
                    for code in unique_codes
                ],
            }
        except BatchClosedError:
            return {
                "success": False,
                "total": len(unique_codes),
                "aggregated": 0,
                "failed": len(unique_codes),
                "errors": [
                    {
                        "code": code,
                        "message": "Batch is closed",
                    }
                    for code in unique_codes
                ],
            }

        cache = RedisCache()
        try:
            await cache.delete(batch_detail_key(batch_id))
            await cache.delete(batch_statistics_key(batch_id))
            await cache.delete(dashboard_key())
        finally:
            await cache.close()

        return {
            "success": True,
            **result.model_dump()
        }
