from fastapi import APIRouter, Depends

from src.api.v1.dependencies import get_analytics_service, get_cache
from src.api.v1.schemas.analytics import DashboardStatisticsResponse
from src.cache.cache_keys import dashboard_key
from src.cache.redis_cache import RedisCache
from src.domain.services.analytics_service import AnalyticsService

router = APIRouter(prefix="/analytics", tags=["Analytics"])


@router.get("/dashboard", response_model=DashboardStatisticsResponse)
async def get_dashboard_statistics(
        service: AnalyticsService = Depends(get_analytics_service),
        cache: RedisCache = Depends(get_cache)
):
    cache_key = dashboard_key()
    cached_statistics = await cache.get(cache_key)
    if cached_statistics is not None:
        return cached_statistics

    statistics = await service.get_dashboard_statistics()
    response = DashboardStatisticsResponse.model_validate(statistics).model_dump(mode="json")

    await cache.set(
        key=cache_key,
        value=response,
        ttl=300
    )
    return response
