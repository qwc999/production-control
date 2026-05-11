from fastapi import APIRouter, Depends, status, HTTPException

from src.api.v1.dependencies import get_batch_service
from src.api.v1.schemas.batch import BatchCreate, BatchResponse, BatchDetailedResponse, BatchUpdate, BatchFilter
from src.api.v1.schemas.product import ProductAggregateResponse, ProductAggregateRequest, ProductAggregateAsyncRequest
from src.api.v1.schemas.reports import BatchReportRequest
from src.api.v1.schemas.tasks import TaskStatusResponse, TaskStartResponse
from src.domain.exceptions.exceptions import BatchAlreadyExistsError, BatchNotFoundError, BatchClosedError
from src.domain.services.batch_service import BatchService
from src.tasks.batch_tasks import aggregate_products_task
from src.tasks.report_tasks import generate_batch_reports_task


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
        return await service.aggregate_products(batch_id, item.unique_codes)
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

@router.post("/{batch_id}/aggregate-async",
             response_model=TaskStatusResponse,
             status_code=status.HTTP_202_ACCEPTED)
async def aggregate_products_async(
        batch_id: int,
        item: ProductAggregateAsyncRequest,
        service: BatchService = Depends(get_batch_service)
):
    try:
        batch = await service.get_batch(batch_id)
    except BatchNotFoundError as e:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail={
                "message": "Batch does not exist"
            }
        ) from e
    if batch.is_closed:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail={
                "message": "BBatch is closed and cannot be edited"
            }
        )

    task = aggregate_products_task.delay(
        batch_id,
        item.unique_codes
    )
    return TaskStartResponse(
        task_id=task.id,
        status="PENDING",
        message="Task started"
    )

@router.post("/{batch_id}/reports",
             response_model=TaskStatusResponse,
             status_code=status.HTTP_202_ACCEPTED)
async def generate_batch_report(
        batch_id: int,
        item: BatchReportRequest,
        service: BatchService = Depends(get_batch_service)
):
    try:
        await service.get_batch(batch_id)
    except BatchNotFoundError as e:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail={"message": "Batch does not exist"},
        ) from e

    task = generate_batch_reports_task.delay(
        batch_id,
        item.format
    )
    return TaskStartResponse(
        task_id=task.id,
        status="PENDING",
        message="Task started"
    )
