from fastapi import APIRouter, status, Depends, HTTPException

from src.api.v1.dependencies import get_product_service
from src.api.v1.schemas.product import ProductResponse, ProductCreate
from src.domain.exceptions.exceptions import ProductAlreadyExistsError, BatchNotFoundError
from src.domain.services.product_service import ProductService

router = APIRouter(prefix="/products", tags=["Product"])


@router.post("",
             response_model=ProductResponse,
             status_code=status.HTTP_201_CREATED)
async def create_product(
        item: ProductCreate,
        service: ProductService = Depends(get_product_service)
):
    try:
        return await service.create_product(item)
    except BatchNotFoundError as e:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail={
                "message": "Batch does not exist"
            }
        ) from e
    except ProductAlreadyExistsError as e:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail={
                "message": "Product already exists"
            }
        ) from e