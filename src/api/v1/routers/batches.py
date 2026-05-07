from fastapi import APIRouter, Depends, status

from src.api.v1.dependencies import get_batch_service
from src.api.v1.schemas.batch import BatchCreate, BatchResponse
from src.domain.services.batch_service import BatchService

router = APIRouter(prefix="/batches", tags=["Batch"])


@router.post("",
             response_model=list[BatchResponse],
             status_code=status.HTTP_201_CREATED)
async def create_batches(
        items: list[BatchCreate],
        service: BatchService = Depends(get_batch_service)
):
    batches = await service.create_batches(items)
    return batches
