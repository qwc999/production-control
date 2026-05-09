from datetime import datetime, timezone

from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import AsyncSession

from src.api.v1.schemas.batch import BatchCreate, BatchUpdate, BatchFilter
from src.api.v1.schemas.product import ProductAggregateResponse, ProductAggregateRequest
from src.data.models.batch import Batch
from src.data.repositories.batch_repository import BatchRepository
from src.data.repositories.product_repository import ProductRepository
from src.data.repositories.work_center_repository import WorkCenterRepository
from src.domain.exceptions.exceptions import BatchAlreadyExistsError, BatchNotFoundError, BatchClosedError


class BatchService:
    def __init__(self, session: AsyncSession):
        self.session = session

        self.batch_repo = BatchRepository(session)
        self.work_center_repo = WorkCenterRepository(session)
        self.product_repo = ProductRepository(session)

    async def get_batch(self, batch_id: int) -> Batch:
        batch = await self.batch_repo.get_by_id_with_products(batch_id)
        if batch is None:
            raise BatchNotFoundError
        return batch

    async def create_batches(self, items: list[BatchCreate]) -> list[Batch]:
        created = []
        for item in items:
            work_center = await self.work_center_repo.get_one_or_create(
                item.work_center_identifier,
                item.work_center_name
            )

            batch_data = {
                "is_closed": item.is_closed,
                "closed_at": datetime.now(timezone.utc) if item.is_closed else None,
                "task_description": item.task_description,
                "work_center_id": work_center.id,
                "shift": item.shift,
                "team": item.team,
                "batch_number": item.batch_number,
                "batch_date": item.batch_date,
                "nomenclature": item.nomenclature,
                "ekn_code": item.ekn_code,
                "shift_start": item.shift_start,
                "shift_end": item.shift_end
            }

            try:
                batch = await self.batch_repo.create(batch_data)
            except IntegrityError as e:
                await self.session.rollback()
                raise BatchAlreadyExistsError() from e

            created.append(batch)
        return created

    async def update_batch(self, batch_id: int, item: BatchUpdate) -> Batch:
        batch = await self.batch_repo.get_by_id(batch_id)
        if batch is None:
            raise BatchNotFoundError

        update_data = item.model_dump(exclude_unset=True, exclude_none=True)
        if "is_closed" in update_data:
            if update_data["is_closed"] is True:
                update_data["closed_at"] = datetime.now(timezone.utc)
            else:
                update_data["closed_at"] = None

        return await self.batch_repo.update(batch, update_data)

    async def filter_batches(self, filters: BatchFilter) -> list[Batch]:
        return await self.batch_repo.get_by_filter(filters)

    async def aggregate_products(self,
                                 batch_id: int,
                                 item: ProductAggregateRequest
                                 ) -> ProductAggregateResponse:
        batch = await self.batch_repo.get_by_id(batch_id)
        if batch is None:
            raise BatchNotFoundError
        if batch.is_closed:
            raise BatchClosedError

        aggregated, errors = 0, []
        products = await self.product_repo.get_by_batch_and_codes(batch_id, item.unique_codes)
        product_by_code = {
            product.unique_code: product for product in products
        }

        for code in item.unique_codes:
            product = product_by_code.get(code)
            if product is None:
                errors.append({
                    "code": code,
                    "message": "Product not found"
                })
                continue
            if product.is_aggregated:
                errors.append({
                    "code": code,
                    "message": "Product is already aggregated"
                })
                continue

            product.is_aggregated = True
            product.aggregated_at = datetime.now(timezone.utc)
            aggregated += 1
        await self.session.commit()

        return ProductAggregateResponse(
            batch_id=batch_id,
            total=len(item.unique_codes),
            aggregated=aggregated,
            failed=len(errors),
            errors=errors
        )
