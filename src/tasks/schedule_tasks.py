import asyncio

from src.api.v1.schemas.analytics import DashboardStatisticsResponse
from src.cache.cache_keys import dashboard_key
from src.cache.redis_cache import RedisCache
from src.domain.services.analytics_service import AnalyticsService
from src.domain.services.schedule_service import ScheduleService
from src.domain.services.storage_cleanup_service import StorageCleanupService
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
        result = await service.auto_close_expired_batches()

        cache = RedisCache()
        try:
            await cache.delete(dashboard_key())
            await cache.delete_pattern("batch_statistics:*")
            await cache.delete_pattern("batches_list:*")
            await cache.delete_pattern("batch_detail:*")
        finally:
            await cache.close()

        return result


@celery_app.task(bind=True,
                 name="schedule.cleanup_old_files")
def cleanup_old_files_task(self):
    service = StorageCleanupService()
    return service.cleanup_old_files()


@celery_app.task(bind=True,
                 name="schedule.update_cached_statistics")
def update_cached_statistics_task(self):
    return asyncio.run(_update_cached_statistics(
        task=self
    ))


async def _update_cached_statistics(task):
    async with celery_async_session_maker() as session:
        service = AnalyticsService(session)
        cache = RedisCache()

        statistics = await service.get_dashboard_statistics()
        response = DashboardStatisticsResponse.model_validate(statistics).model_dump(mode="json")

        try:
            await cache.set(
                key=dashboard_key(),
                value=response,
                ttl=300
            )
        finally:
            await cache.close()

        return response
