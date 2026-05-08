from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import AsyncSession

from src.api.v1.schemas.product import ProductCreate
from src.data.models import Product
from src.data.repositories.batch_repository import BatchRepository
from src.data.repositories.product_repository import ProductRepository
from src.domain.exceptions.exceptions import BatchNotFoundError, ProductAlreadyExistsError


class ProductService:
    def __init__(self, session: AsyncSession):
        self.session = session

        self.batch_repo = BatchRepository(session)
        self.product_repo = ProductRepository(session)

    async def create_product(self, item: ProductCreate) -> Product:
        batch = await self.batch_repo.get_by_id(item.batch_id)
        if batch is None:
            raise BatchNotFoundError

        product_data = {
            "batch_id": item.batch_id,
            "unique_code": item.unique_code
        }

        try:
            return await self.product_repo.create(product_data)
        except IntegrityError as e:
            await self.session.rollback()
            raise ProductAlreadyExistsError() from e
