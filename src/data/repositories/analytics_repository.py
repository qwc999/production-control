from datetime import datetime

from sqlalchemy import select, func, distinct, case
from sqlalchemy.ext.asyncio import AsyncSession

from src.data.models import Batch, Product, WorkCenter


class AnalyticsRepository:
    def __init__(self, session: AsyncSession):
        self.session = session

    async def count_batches(self) -> dict:
        total_query = select(func.count(Batch.id))
        active_query = select(func.count(Batch.id)).where(Batch.is_closed.is_(False))
        closed_query = select(func.count(Batch.id)).where(Batch.is_closed.is_(True))

        total = await self.session.scalar(total_query)
        active = await self.session.scalar(active_query)
        closed = await self.session.scalar(closed_query)

        return {
            "total": total,
            "active": active,
            "closed": closed
        }

    async def count_products(self) -> dict:
        total_query = select(func.count(Product.id))
        aggregated_query = select(func.count(Product.id)).where(Product.is_aggregated.is_(True))

        total = await self.session.scalar(total_query)
        aggregated = await self.session.scalar(aggregated_query)

        return {
            "total": total,
            "aggregated": aggregated,
        }

    async def count_today(self, day: datetime) -> dict:
        batches_created_query = select(func.count(Batch.id).where(Batch.created_at >= day))
        batches_closed_query = select(func.count(Batch.id).where(Batch.closed_at >= day))
        products_added_query = select(func.count(Product.id).where(Product.created_at >= day))
        products_aggregated_query = select(func.count(Product.id).where(Product.aggregated_at >= day))

        batches_created = await self.session.scalar(batches_created_query)
        batches_closed = await self.session.scalar(batches_closed_query)
        products_added = await self.session.scalar(products_added_query)
        products_aggregated = await self.session.scalar(products_aggregated_query)

        return {
            "batches_created": batches_created,
            "batches_closed": batches_closed,
            "products_added": products_added,
            "products_aggregated": products_aggregated
        }

    async def get_stats_by_shift(self) -> dict:
        query = (
            select(
                Batch.shift,
                func.count(distinct(Batch.id)).label("batches"),
                func.count(Product.id).label("products"),
                func.count(Product.id).where(Product.is_aggregated.is_(True)).label("aggregated")
            )
            .select_from(Batch).outerjoin(Product, Product.batch_id == Batch.id)
            .group_by(Batch.shift)
            .order_by(Batch.shift)
        )
        result = await self.session.execute(query)

        return {
            row.shift: {
                "batches": row.batches,
                "products": row.products,
                "aggregated": row.aggregated
            }
            for row in result.all()
        }

    async def get_top_work_centers(self, limit: int = 5) -> list[dict]:
        query = (
            select(
                WorkCenter.identifier,
                WorkCenter.name,
                func.count(distinct(Batch.id)).label("batches_count"),
                func.count(Product.id).label("products_count"),
                func.coalesce(func.sum(
                    case((Product.is_aggregated.is_(True), 1),
                    else_=0,
                ), 0)).label("aggregated_products")
            )
            .select_from(WorkCenter)
            .join(Batch, Batch.work_center_id == WorkCenter.id)
            .outerjoin(Product, Product.batch_id == Batch.id)
            .group_by(func.count(distinct(Batch.id)).desc())
            .limit(limit)
        )
        result = await self.session.execute(query)

        rows = []
        for row in result.all():
            aggregation_rate = (round(row.aggregated_products / row.products_count * 100, 2)
                                if row.products_count else 0)
            rows.append(
                {
                    "id": row.identifier,
                    "name": row.name,
                    "batches_count": row.batches_count,
                    "products_count": row.products_count,
                    "aggregation_rate": aggregation_rate
                }
            )
            return rows

    async def count_products_by_batch(self, batch_id: int) -> dict:
        total_query = (select(func.count(Product.id).where(Product.batch_id == batch_id)))
        aggregated_query = (select(func.count(Product.id).where(Product.batch_id == batch_id))
                            .where(Product.is_aggregated.is_(True)))

        total = await self.session.scalar(total_query)
        aggregated = await self.session.scalar(aggregated_query)

        return {
            "total": total,
            "aggregated": aggregated
        }