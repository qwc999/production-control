from datetime import datetime, timezone, timedelta

from sqlalchemy.ext.asyncio import AsyncSession

from src.data.repositories.analytics_repository import AnalyticsRepository
from src.data.repositories.batch_repository import BatchRepository
from src.domain.exceptions.exceptions import BatchNotFoundError


class AnalyticsService:
    def __init__(self, session: AsyncSession):
        self.session = session
        self.analytics_repo = AnalyticsRepository(session)
        self.batch_repo = BatchRepository(session)

    async def get_dashboard_statistics(self) -> dict:
        now = datetime.now(timezone.utc)
        start_of_day = now.replace(hour=0, minute=0, second=0, microsecond=0)

        batch_count = await self.analytics_repo.count_batches()
        product_count = await self.analytics_repo.count_products()
        today = await self.analytics_repo.count_today(start_of_day)
        by_shift = await self.analytics_repo.get_stats_by_shift()
        top_work_centers = await self.analytics_repo.get_top_work_centers()

        aggregation_rate = (round(product_count["aggregated"] / product_count["total"] * 100, 2)
                            if product_count["total"] else 0)

        return {
            "summary": {
                "total_batches": batch_count["total"],
                "active_batches": batch_count["active"],
                "closed_batches": batch_count["closed"],
                "total_products": product_count["total"],
                "aggregated_products": product_count["aggregated"],
                "aggregation_rate": aggregation_rate
            },
            "today": today,
            "by_shift": by_shift,
            "top_work_centers": top_work_centers,
            "cached_at": now
        }

    async def get_batch_statistics(self, batch_id: int) -> dict:
        batch = await self.batch_repo.get_by_id(batch_id)
        if not batch:
            raise BatchNotFoundError()

        product_count = await self.analytics_repo.count_products_by_batch(batch_id)

        total_products = product_count["total"]
        aggregated = product_count["aggregated"]
        remaining = total_products - aggregated
        aggregation_rate = (round(aggregated / total_products * 100, 2)
                            if total_products else 0)
        now = datetime.now(timezone.utc)
        shift_end, shift_start = batch.shift_end, batch.shift_start
        shift_duration_hours = round((shift_end - shift_start).total_seconds() / 3600, 2)
        elapsed_hours = round((min(now, shift_end) - shift_start).total_seconds() / 3600, 2)
        products_per_hour = (round(aggregated / elapsed_hours, 2)
                             if elapsed_hours > 0 else 0)

        estimated_completion = None
        if products_per_hour > 0 and remaining > 0:
            estimated_completion = now + timedelta(hours=remaining / products_per_hour)
        elif remaining == 0:
            estimated_completion = now

        return {
            "batch_info": {
                "id": batch_id,
                "team": batch.team,
                "batch_number": batch.batch_number,
                "batch_date": batch.batch_date,
                "is_closed": batch.is_closed
            },
            "production_stats": {
                "total_products": total_products,
                "aggregated": aggregated,
                "remaining": remaining,
                "aggregation_rate": aggregation_rate
            },
            "timeline": {
                "shift_duration_hours": shift_duration_hours,
                "elapsed_hours": elapsed_hours,
                "products_per_hour": products_per_hour,
                "estimated_completion": estimated_completion
            }
        }
