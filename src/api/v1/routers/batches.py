from fastapi import APIRouter, Depends, status, HTTPException

from src.api.v1.dependencies import get_batch_service
from src.api.v1.schemas.batch import BatchCreate, BatchResponse, BatchDetailedResponse, BatchUpdate, BatchFilter
from src.api.v1.schemas.product import ProductAggregateResponse, ProductAggregateRequest
from src.domain.exceptions.exceptions import BatchAlreadyExistsError, BatchNotFoundError, BatchClosedError
from src.domain.services.batch_service import BatchService

router = APIRouter(prefix="/batches", tags=["Batch"])


@router.post("",
             response_model=list[BatchResponse],
             status_code=status.HTTP_201_CREATED)
async def create_batches(
        items: list[BatchCreate],
        service: BatchService = Depends(get_batch_service)
):
    try:
        batches = await service.create_batches(items)
        return batches
    except BatchAlreadyExistsError as e:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail={
                "message": "Batch already exists"
            }
        ) from e

@router.get("/{batch_id}",
            response_model=BatchDetailedResponse)
async def get_batch(
        batch_id: int,
        service: BatchService = Depends(get_batch_service)
):
    try:
        return await service.get_batch(batch_id)
    except BatchNotFoundError as e:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail={
                "message": "Batch does not exist"
            }
        ) from e

@router.patch("/{batch_id}",
            response_model=BatchResponse)
async def update_batch(
        batch_id: int,
        item: BatchUpdate,
        service: BatchService = Depends(get_batch_service)
):
    try:
        return await service.update_batch(batch_id, item)
    except BatchNotFoundError as e:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail={
                "message": "Batch does not exist"
            }
        ) from e

@router.get("",
            response_model=list[BatchResponse])
async def get_batches(
        filters: BatchFilter = Depends(),
        service: BatchService = Depends(get_batch_service)
):
    return await service.filter_batches(filters)

@router.post("/{batch_id}/aggregate",
             response_model=ProductAggregateResponse)
async def aggregate_products(
        batch_id: int,
        item: ProductAggregateRequest,
        service: BatchService = Depends(get_batch_service)
):
    try:
        return await service.aggregate_products(batch_id, item)
    except BatchNotFoundError as e:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail={
                "message": "Batch does not exist"
            }
        ) from e
    except BatchClosedError as e:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail={
                "message": "BBatch is closed and cannot be edited"
            }
        ) from e
